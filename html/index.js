var React = require('react');
var ReactDOM = require('react-dom');
var $ = require('jquery');
var _ = require('lodash');
var querystring = require('querystring');
var BS = require('react-bootstrap');
var Map = require('react-leaflet').Map;
var TileLayer = require('react-leaflet').TileLayer;
var Leaflet = require('react-leaflet');
var Promise = (window && window.Promise) || require('promise-js');
var Forms = require('./forms');

var ViewShed = React.createClass({
  getInitialState: function(){
    return {
      lat:51.505,
      lng:-0.09,
      submitDisabled:true,
      radius:100
    }
  },
  disableSubmit: function(){
    this.setState({submitDisabled: true});
  },
  onValid: _.debounce(function(){
    var values = this.refs.form.getCurrentValues();
    console.log(values);
    this.setState({
      lat: parseFloat(values.lat),
      lng: parseFloat(values.lng),
      submitDisabled: false,
      radius: parseFloat(values.radius)
    });
  }, 750),
  //dblclick
  //getLeafletElement
  render: function(){
    var latlng = [this.state.lat, this.state.lng];
    var submitClass = this.state.submitDisabled ? "btn btn-disabled" : "btn btn-primary";
    return (
      <BS.Grid fluid={true} style={{height:"100%"}}>
        <BS.Row>
          <Formsy.Form style={{padding:"2px"}} ref="form" onValid={this.onValid} onInvalid={this.disableSubmit}>
            <BS.Col md={4}><
              Forms.GeocodingInput name="place"></Forms.GeocodingInput>
            </BS.Col>
            <BS.Col md={2}>
              <Forms.LatInput name="lat" required={true}></Forms.LatInput>
            </BS.Col>
            <BS.Col md={2}>
              <Forms.LngInput name="lng" required={true}></Forms.LngInput>
            </BS.Col>
            <BS.Col md={2}>
              <Forms.TextInput name="radius" placeholder="radius" value={this.state.radius} required={true}
                validations='isInt,isGreaterThanOrEqual:10,isLessThanOrEqual:1000'
                validationErrors={{
                  isInt:'radius must an whole number',
                  isGreaterThanOrEqual:'radius must be greater than 10',
                  isLessThanOrEqual:'radius must be less than 1000'
                }}>
              </Forms.TextInput>
            </BS.Col>
            <BS.Col md={2}>
              <button style={{width:"100%"}} className={submitClass} type="submit" disabled={this.state.submitDisabled}>Compute Viewshed</button>
            </BS.Col>
          </Formsy.Form>  
        </BS.Row>
        <BS.Row style={{height:"100%"}}>
          <BS.Col md={12} style={{height:"100%"}}>
            <Map center={latlng} zoom={12} style={{height:"100%"}}>
              <TileLayer url='http://{s}.tile.osm.org/{z}/{x}/{y}.png' attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'/>
              <Leaflet.CircleMarker radius={this.state.radius} center={latlng}></Leaflet.CircleMarker>
            </Map>
          </BS.Col>
        </BS.Row>
      </BS.Grid>
    )
  }
});

//Render when body loaded
$(function(){ReactDOM.render(<ViewShed/>, document.getElementById("application"));})
//export some things to window
_.extend(window || {}, {
  '_':_,
  '$':$,
  Promise:Promise,
  ReactDOM:ReactDOM
});