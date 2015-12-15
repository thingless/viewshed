var React = require('react');
var ReactDOM = require('react-dom');
var $ = require('jquery');
var _ = require('lodash');
var Alert = require('react-bootstrap').Alert;
var Grid = require('react-bootstrap').Grid;
var Row = require('react-bootstrap').Row;
var Col = require('react-bootstrap').Col;
var Map = require('react-leaflet').Map;
var TileLayer = require('react-leaflet').TileLayer;

var ViewShed = React.createClass({
  render: function(){
    return (
      <Grid>
        <Row>
          <Col md={8}><code>&lt;{'Col xs={12} md={8}'} /&gt;</code></Col>
          <Col md={4}><code>&lt;{'Col xs={6} md={4}'} /&gt;</code></Col>
        </Row>
        <Row>
          <Col md={12}>
            <Map center={[51.505, -0.09]} zoom={12}>
              <TileLayer url='http://{s}.tile.osm.org/{z}/{x}/{y}.png' attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'/>
            </Map>
          </Col>
        </Row>
      </Grid>
    )
  }
});

$(function(){ReactDOM.render(<ViewShed/>, document.getElementById("application"));})