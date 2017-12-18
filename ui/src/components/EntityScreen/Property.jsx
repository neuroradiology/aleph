import {FormattedMessage} from 'react-intl';
import React, { Component } from 'react';
import { connect } from 'react-redux';

import getHost from 'src/util/getHost';
import Country from 'src/components/common/Country';


class Value extends Component {
  render() {
    const { value, model } = this.props;
    if (!value) {
        return null;
    }
    if (model.type === 'country') {
        return (<Country.Name code={value} />);
    }
    if (model.type === 'url' || model.type === 'uri') {
        // TODO: add external link icon?
        return (
            <a href={value} target='_blank'>
                <i className="fa fa-external-link-square" aria-hidden="true"></i>
                { getHost(value) }
            </a>
        );
    }
    // if (model.type === 'entity') {
    //     return (<span>ENTITY</span>);
    // }
    return (
      <span>{value}</span>
    );
  }
}

class Name extends Component {
  render() {
    const { name, model } = this.props,
          label = model.label || name;

    return (
      <span>{label}</span>
    );
  }
}

class Table extends Component {
  render() {
    const { properties, schema, schemata, children } = this.props,
          model = schemata[schema] || {};
    
    const items = Object.entries(properties).map(([name, values]) => {
        const propModel = model.properties[name];
        if (propModel && !propModel.hidden && values.length) {
            return (
                <tr key={`${name}`}>
                    <th>
                        <Name name={name} model={propModel} />
                    </th>
                    <td>
                        { values.map((value, i) => {
                            return (<Value key={`value-${i}`} value={value} model={propModel} />)
                        }) }
                    </td>
                </tr>
            )
        }
        return null;
    });

    return (
      <table className="pt-table">
        <tbody>
            {items}
            {children}
        </tbody>
      </table>
    );
  }
}

const mapStateToProps = (state, ownProps) => {
  return {
    schemata: state.metadata.schemata
  };
}

class Property extends Component {
  static Name = Name;
  static Value = Value;
  static Table = connect(mapStateToProps)(Table);
}

export default Property;
