// @ts-ignore
import Property from './property.ts';

interface ILabelReadingConfiguration {
  forcePlural: boolean
}

interface IProperties {
  [x: string]: Property,
}


export default class Schema {
  private readonly name: string;
  private readonly label: string;
  private readonly plural: string;
  public readonly icon: string;
  private readonly featured: Array<string>;
  public properties: IProperties = new Map();
  private readonly DOCUMENT_SCHEMATA: string[] = [
    'Document', 'Pages', 'Folder',
    'Package', 'Email', 'HyperText',
    'Workbook', 'Table', 'PlainText',
    'Image', 'Video', 'Audio'
  ];

  static hasSchemata(document, schemata:string[]):boolean{
    if(document){
      return !!schemata.find(schema => !!~document.schemata.indexOf(schema))
    }
    return false;
  }
  constructor(schemaName, theImplementation) {
    this.name = schemaName;
    this.label = theImplementation.label;
    this.plural = theImplementation.plural;
    this.icon = theImplementation.icon;
    this.featured = theImplementation.featured;
    Object
      .entries(theImplementation.properties)
      .forEach(([propertyName, property]) => {
        this.properties.set(propertyName, new Property(property, this))
      })
  }

  getLabel({forcePlural}: ILabelReadingConfiguration) {
    let label = this.label || this.name;
    if (forcePlural || this.plural) {
      label = this.plural || label;
    }
    return label;
  }

  reverseLabel(reference) {
    if (!reference || !reference.property) {
      return null;
    }
    const prop = reference.property;
    const reverse = this.properties.get(prop.reverse) || prop;
    return reverse.label;
  };

  isFeaturedProp(propertyName){
    return !!~this.featured.indexOf(propertyName)
  }

  isDocumentSchema():boolean{
    return !!~this.DOCUMENT_SCHEMATA.indexOf(this.name)
  }

  getEntityProperties(entity:Schema):Property[]{
    return this.getFeaturedProperties()
      .filter(property => {
        return !property.caption && entity.properties[property.name]
      })
  }

  getFeaturedProperties(){
    return this.featured
      .map(featuredPropertyName=> this.properties.get(featuredPropertyName))
  }

  extends(schemaName):boolean{
    /*FIXME: Include parent schema name*/
   return !!Array.from(this.properties.values())
     .find((property:Property) => property.extends(schemaName))
  }

}