var React = require('react');
var ReactDOM = require('react-dom');
var $ = require('jquery');
var _ = require('lodash');
var querystring = require('querystring');
var BS = require('react-bootstrap');
var Map = require('react-leaflet').Map;
var TileLayer = require('react-leaflet').TileLayer;
var Promise = (window && window.Promise) || require('promise-js');
var Forms = require('./forms');

var ViewShed = React.createClass({
  render: function(){
    return (
      <BS.Grid fluid={true} style={{height:"100%"}}>
        <Formsy.Form>
          <BS.Row>
            <BS.Col md={4}><
              Forms.GeocodingInput name="place"></Forms.GeocodingInput>
            </BS.Col>
            <BS.Col md={3}>
              <Forms.LatInput name="lat"></Forms.LatInput>
            </BS.Col>
            <BS.Col md={3}>
              <Forms.LngInput name="lng"></Forms.LngInput>
            </BS.Col>
            <BS.Col md={2}>
              <button className="btn btn-primary" type="submit">Compute Viewshed</button>
            </BS.Col>
          </BS.Row>
        </Formsy.Form>
        <BS.Row style={{height:"100%"}}>
          <BS.Col md={12} style={{height:"100%"}}>
            <Map center={[51.505, -0.09]} zoom={12} style={{height:"100%"}}>
              <TileLayer url='http://{s}.tile.osm.org/{z}/{x}/{y}.png' attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'/>
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