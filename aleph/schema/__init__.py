from aleph.util import dict_list, ensure_list
from aleph.text import string_value
from aleph.schema.types import resolve_type


class SchemaValidationException(Exception):
    """Schema validation errors will be caught by the API."""

    def __init__(self, errors):
        self.errors = errors
        super(SchemaValidationException, self).__init__(repr(errors))


class SchemaProperty(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.name = name.strip()
        self.data = data
        self.label = data.get('label', name)
        self.is_hidden = data.get('hidden', False)
        self.is_multiple = data.get('multiple', False)
        self.is_required = data.get('required', False)
        self.is_label = name == 'name'
        cls = resolve_type(data.get('type', 'string'))
        self.type = cls()

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        value, error = [], None
        for val in ensure_list(data):
            val = string_value(val)
            if val is None:
                continue
            if self.type.normalize_value(val) is None:
                error = "Invalid value"
            value.append(val)
        if not self.is_multiple:
            value = value[0] if len(value) else None
        if self.is_required and (value is None or not len(value)):
            error = "Field is required."
        return value, error

    def __repr__(self):
        return '<SchemaProperty(%r, %r)>' % (self.schema, self.name)


class Schema(object):
    """Defines the abstract data model.

    Schema items define the entities and links available in the model.
    """

    ENTITY = 'entities'
    LINK = 'links'
    SECTIONS = [ENTITY, LINK]

    def __init__(self, model, section, name, data):
        assert section in self.SECTIONS, section
        self.model = model
        self.section = section
        self.name = name
        self.data = data
        self.label = data.get('label', name)
        self.icon = data.get('icon')
        self.is_hidden = data.get('hidden', False)
        self._extends = dict_list(data, 'extends')
        self._own_properties = []
        for name, prop in data.get('properties', {}).items():
            self._own_properties.append(SchemaProperty(self, name, prop))

        if section == self.LINK:
            # links only:
            self.forward = data.get('forward', self.label)
            self.reverse = data.get('reverse', self.label)

    @property
    def extends(self):
        """Return the inherited schemata."""
        for base in self._extends:
            yield self.model.get(self.section, base)

    @property
    def schemata(self):
        """Return the full inheritance chain."""
        yield self
        for base in self.extends:
            for schema in base.schemata:
                yield schema

    @property
    def properties(self):
        """Return properties, those defined locally and in ancestors."""
        for prop in self._own_properties:
            yield prop
        for schema in self.extends:
            for prop in schema.properties:
                yield prop

    def get(self, name):
        for prop in self.properties:
            if prop.name == name:
                return prop
        raise ValueError("[%r] missing property: %s" % (self, name))

    def validate(self, data):
        """Validate a dataset against the given schema.

        This will also drop keys which are not present as properties.
        """
        result = {}
        errors = {}
        for prop in self.properties:
            value = data.get(prop.name)
            value, error = prop.validate(value)
            if error is not None:
                errors[prop.name] = error
            elif value is not None:
                result[prop.name] = value
        if len(errors):
            raise SchemaValidationException(errors)
        return result

    def __repr__(self):
        return '<Schema(%r)>' % self.name


class SchemaSet(object):
    """A collection of schemata."""

    def __init__(self, data):
        self.schemata = []
        for section in Schema.SECTIONS:
            for name, sconfig in data.get(section, {}).items():
                self.schemata.append(Schema(self, section, name, sconfig))

    def get(self, section, name):
        for schema in self.schemata:
            if schema.section == section and schema.name == name:
                return schema
        raise TypeError("No such schema for %s: %s" % (section, name))

    def merge_entity_schema(self, left, right):
        """Select the most narrow of two schemata.

        When indexing data from a dataset, an entity may be declared as a
        LegalEntity in one query, and as a Person in another. This function
        will select the most specific of two schemata offered. In the example,
        that would be Person.
        """
        if left == right:
            return left
        lefts = self.get(Schema.ENTITY, left)
        lefts = [s.name for s in lefts.schemata]
        if right in lefts:
            return left

        rights = self.get(Schema.ENTITY, right)
        rights = [s.name for s in rights.schemata]
        if left in rights:
            return right

        for left in lefts:
            for right in rights:
                if left == right:
                    return left

    def __repr__(self):
        return '<SchemaSet(%r)>' % self.schemata
