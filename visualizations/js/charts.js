'use strict';

var _chart     = null;
var _chartData = null;

var BAR_COLORS = [
  '#b71c1c', '#e53935', '#fb8c00', '#fdd835', '#7cb342',
  '#42a5f5', '#1976d2', '#0d47a1', '#0c2461', '#0c2461',
];

function initChart(data) {
  _chartData = data.bar_charts;

  var ctx = document.getElementById('bar-chart').getContext('2d');

  _chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels:   [],
      datasets: [{
        data:            [],
        backgroundColor: BAR_COLORS,
        borderWidth:     0,
        borderRadius:    3,
      }],
    },
    options: {
      indexAxis:   'y',
      responsive:  true,
      maintainAspectRatio: false,
      animation: { duration: 400, easing: 'easeInOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              return ' ' + ctx.parsed.x.toLocaleString() + ' incidents';
            },
          },
          backgroundColor: '#ffffff',
          borderColor:     '#cfd8dc',
          borderWidth:     1,
          titleColor:      '#263238',
          bodyColor:       '#607d8b',
        },
      },
      scales: {
        x: {
          grid:  { color: '#eceff1' },
          ticks: { color: '#607d8b', font: { size: 9 },
                   callback: function(v) { return v.toLocaleString(); } },
          border: { color: '#cfd8dc' },
        },
        y: {
          grid:  { display: false },
          ticks: { color: '#263238', font: { size: 10 } },
          border: { color: '#cfd8dc' },
        },
      },
    },
  });


  updateChart('2013');
  document.addEventListener('app:update', function(e) {
    updateChart(e.detail.year);
  });
}

function updateChart(year) {
  if (!_chart || !_chartData) return;

  var entry = _chartData[year];
  if (!entry) return;

  _chart.data.labels          = entry.cities.slice().reverse();
  _chart.data.datasets[0].data = entry.counts.slice().reverse();
  _chart.update('active');
  var titleEl = document.getElementById('chart-panel-title');
  if (titleEl) titleEl.textContent = 'Top 10 Cities — ' + year;
}

window.initChart = initChart;
