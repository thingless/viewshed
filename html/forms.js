var React = require('react');
var ReactDOM = require('react-dom');
var Formsy = require('formsy-react');
var _ = require('lodash');

Formsy.addValidationRule('isGreaterThanOrEqual', function (values, value, number) {
  if(!value && value!==0){ return true; }
  return parseFloat(value) >= parseFloat(number);
});
Formsy.addValidationRule('isLessThanOrEqual', function (values, value, number) {
  if(!value && value!==0){ return true; }
  return parseFloat(value) <= parseFloat(number);
});

var LatInput = React.createClass(_.extend({}, Formsy.Mixin, {
  changeValue: function (event) {
    this.setValue(event.currentTarget.value);
  },
  getDefaultProps: function(){
    return {
      validations:'isNumeric,isGreaterThanOrEqual:-85.05,isLessThanOrEqual:85.05',
      validationErrors:{
        isNumeric:'latitude must be a number',
        isGreaterThanOrEqual:'latitude must be greater than -85.05',
        isLessThanOrEqual:'latitude must be less than 85.05'
      }
    }
  },
  render: function () {
    return (
      <div className={this.showRequired() || this.showError() ? 'form-group has-error' : 'form-group'}>
        <div className="input-group">
          <span className="input-group-addon">Lat</span>
          <input type="text" className="form-control" placeholder="latitude" onChange={this.changeValue} value={this.getValue()}></input>
        </div>
        <span className="help-block">{this.getErrorMessage()}</span>
      </div>
    );
  }
}));

var TextInput = React.createClass(_.extend({}, Formsy.Mixin, {
  changeValue: function (event) {
    this.setValue(event.currentTarget.value);
  },
  render: function () {
    return (
      <div className={this.showRequired() || this.showError() ? 'form-group has-error' : 'form-group'}>
        <div className="input-group">
          <span className="input-group-addon">{this.props.placeholder || ''}</span>
          <input type="text" className="form-control" placeholder={this.props.placeholder || ''} onChange={this.changeValue} value={this.getValue()}></input>
        </div>
        <span className="help-block">{this.getErrorMessage()}</span>
      </div>
    );
  }
}));

var LngInput = React.createClass(_.extend({}, Formsy.Mixin, {
  changeValue: function (event) {
    this.setValue(event.currentTarget.value);
  },
  getDefaultProps: function(){
    return {
      validations:'isNumeric,isGreaterThanOrEqual:-180,isLessThanOrEqual:180',
      validationErrors:{
        isNumeric:'longitude must be a number',
        isGreaterThanOrEqual:'longitude must be greater than -180',
        isLessThanOrEqual:'longitude must be less than 180'
      }
    }
  },
  render: function () {
    return (
      <div className={this.showRequired() || this.showError() ? 'form-group has-error' : 'form-group'}>
        <div className="input-group">
          <span className="input-group-addon">Lng</span>
          <input type="text" className="form-control" placeholder="longitude" onChange={this.changeValue} value={this.getValue()}></input>
        </div>
        <span className="help-block">{this.getErrorMessage()}</span>
      </div>
    );
  }
}));

module.exports = {
  LatInput:LatInput,
  LngInput:LngInput,
  TextInput:TextInput
};

/*
function geocoding(searchTerm){
  return new Promise(function(resolve, reject) {
    var url = 'http://nominatim.openstreetmap.org/search.php?' + querystring.stringify({
      q:searchTerm,
      format:'jsonv2'
    });
    $.ajax(url, {error:reject, success:resolve});
  });
}

function reverseGeocoding(lon, lat){
  return new Promise(function(resolve, reject) {
    var url = 'http://nominatim.openstreetmap.org/reverse?' + querystring.stringify({
      format:'jsonv2',
      lat:lat,
      lon:lon
    });
    $.ajax(url, {error:reject, success:resolve});
  });
}
*/
