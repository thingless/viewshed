var React = require('react');
var ReactDOM = require('react-dom');
var $ = require('jquery');
var _ = require('lodash');
var querystring = require('querystring');
var Alert = require('react-bootstrap').Alert;
var Grid = require('react-bootstrap').Grid;
var Row = require('react-bootstrap').Row;
var Col = require('react-bootstrap').Col;
var Map = require('react-leaflet').Map;
var TileLayer = require('react-leaflet').TileLayer;
var Promise = (window && window.Promise) || require('promise-js');

function geocoding(searchTerm){
  return new Promise(function(resolve, reject) {
    var url = 'http://nominatim.openstreetmap.org/search.php?' + querystring.stringify({
      q:searchTerm,
      format:'jsonv2'
    });
    $.ajax(url, {error:reject, success:resolve });
  });
}

var ViewShed = React.createClass({
  render: function(){
    return (
      <Grid fluid={true} style={{height:"100%"}}>
        <Row>
          <Col md={8}><code>&lt;{'Col xs={12} md={8}'} /&gt;</code></Col>
          <Col md={4}><code>&lt;{'Col xs={6} md={4}'} /&gt;</code></Col>
        </Row>
        <Row style={{height:"100%"}}>
          <Col md={12} style={{height:"100%"}}>
            <Map center={[51.505, -0.09]} zoom={12} style={{height:"100%"}}>
              <TileLayer url='http://{s}.tile.osm.org/{z}/{x}/{y}.png' attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'/>
            </Map>
          </Col>
        </Row>
      </Grid>
    )
  }
});

//Render when body loaded
$(function(){ReactDOM.render(<ViewShed/>, document.getElementById("application"));})
//export some things to window
_.extend(window || {}, {
  '_':_,
  'geocoding':geocoding,
  '$':$,
  'Promise':Promise
});