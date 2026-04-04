'use strict';

var _map         = null;
var _heatLayer   = null;
var _crimeData   = null;

var GRADIENTS = {
  All: {
    0.1:  '#0c2461',
    0.35: '#1565c0',
    0.55: '#2e7d32',
    0.72: '#fdd835',
    0.88: '#fb8c00',
    1.0:  '#b71c1c',
  },
  Violent: {
    0.1:  '#3e2723',
    0.35: '#c62828',
    0.55: '#e53935',
    0.75: '#ff9800',
    0.9:  '#ffeb3b',
    1.0:  '#fff9c4',
  },
  Property: {
    0.1:  '#0d47a1',
    0.35: '#1976d2',
    0.55: '#42a5f5',
    0.72: '#81d4fa',
    0.88: '#fff59d',
    1.0:  '#ff9800',
  },
  Drugs: {
    0.1:  '#1b5e20',
    0.35: '#388e3c',
    0.55: '#7cb342',
    0.72: '#cddc39',
    0.88: '#fbc02d',
    1.0:  '#d84315',
  },
};

var CITY_MARKERS = [
  { lat: 40.7608, lon: -111.8910, name: 'Salt Lake City' },
  { lat: 40.3916, lon: -111.8508, name: 'Lehi' },
  { lat: 40.6461, lon: -111.4980, name: 'Park City' },
  { lat: 40.5621, lon: -111.9294, name: 'South Jordan' },
  { lat: 40.7182, lon: -111.8882, name: 'S. Salt Lake' },
  { lat: 41.2230, lon: -111.9738, name: 'Ogden' },
  { lat: 40.2338, lon: -111.6585, name: 'Provo' },
];

function initMap(data) {
  _crimeData = data;

  _map = L.map('map', {
    center:  [40.58, -111.85],
    zoom:    9,
    zoomControl: true,
  });

  L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    { maxZoom: 19, subdomains: 'abcd' }
  ).addTo(_map);

  CITY_MARKERS.forEach(function(city) {
    var icon = L.divIcon({
      className: '',
      html: '<div style="'
          + 'color:#263238;font-size:10px;font-family:Segoe UI,sans-serif;'
          + 'background:rgba(255,255,255,0.92);padding:2px 5px;border-radius:3px;'
          + 'white-space:nowrap;border:1px solid #b0bec5;box-shadow:0 1px 2px rgba(0,0,0,0.12);pointer-events:none'
          + '">' + city.name + '</div>',
      iconAnchor: [0, 0],
    });
    L.marker([city.lat, city.lon], { icon: icon }).addTo(_map);
  });

  updateHeatmap('2013', 'All');
  document.addEventListener('app:update', function(e) {
    updateHeatmap(e.detail.year, e.detail.category);
  });
}

function updateHeatmap(year, category) {
  if (!_crimeData) return;

  if (_heatLayer) {
    _map.removeLayer(_heatLayer);
    _heatLayer = null;
  }

  var pts = (_crimeData.heatmap[category] || {})[year] || [];

  _heatLayer = L.heatLayer(pts, {
    minOpacity: 0.35,
    radius:     18,
    blur:       22,
    maxZoom:    14,
    gradient:   GRADIENTS[category] || GRADIENTS['All'],
  });
  _heatLayer.addTo(_map);
}

window.initMap = initMap;
