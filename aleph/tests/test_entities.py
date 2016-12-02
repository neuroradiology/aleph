# coding: utf-8
import json
from pprint import pprint
from apikit import jsonify

from aleph.core import db
from aleph.model import Collection, Entity, Alert
# from aleph.model.entity_details import EntityAddress
from aleph.tests.util import TestCase


class EntitiesTestCase(TestCase):

    def setUp(self):
        super(EntitiesTestCase, self).setUp()
        self.rolex = self.create_user(foreign_id='user_3')
        self.col = Collection()
        self.col.label = 'Original Collection'
        self.col.foreign_id = 'test_coll_entities'
        db.session.add(self.col)
        self.col_other = Collection()
        self.col_other.label = 'Other Collection'
        self.col_other.foreign_id = 'test_coll_entities_other'
        db.session.add(self.col_other)
        db.session.flush()
        self.ent = Entity.save({
            '$schema': 'LegalEntity',
            'name': 'Winnie the Pooh',
            'country': 'pa',
            'summary': 'a fictional teddy bear created by author A. A. Milne',
            'alias': [u'Puh der Bär', 'Pooh Bear']
        }, self.col)
        db.session.add(self.ent)
        db.session.flush()
        self.other = Entity.save({
            '$schema': 'LegalEntity',
            'name': 'Pu der Bär',
            'country': 'de',
            'description': 'he is a bear',
            'alias': [u'Puh der Bär']
        }, self.col)
        db.session.add(self.other)
        self.alert = Alert()
        self.alert.entity = self.other
        db.session.add(self.alert)
        db.session.commit()

    def test_merge(self):
        self.ent.merge(self.other)
        db.session.flush()
        data = json.loads(jsonify(self.ent).data)
        assert 'bear' in data['description'], data
        assert 'pa' in data['country'], data
        db.session.refresh(self.alert)
        assert self.alert.label == data['name']
        assert self.other.deleted_at is not None, self.other

    def test_api_merge(self):
        url = '/api/1/entities/%s/merge/%s' % (self.ent.id, self.other.id)
        res = self.client.delete(url, data={}, content_type='application/json')
        assert res.status_code == 403, res.json
        self.login(is_admin=True)
        res = self.client.delete(url, data={}, content_type='application/json')
        data = res.json
        assert 'bear' in data['description']
        assert 'pa' in data['country']
