'use strict';

window.AppState = { year: '2013', category: 'All' };

function setState(updates) {
  Object.assign(window.AppState, updates);
  document.dispatchEvent(
    new CustomEvent('app:update', { detail: Object.assign({}, window.AppState) })
  );
  _updateStats(window.AppState.year, window.AppState.category, window._crimeData);
}
function initControls(data) {
  window._crimeData = data;

  var select  = document.getElementById('year-select');
  var btnPrev = document.getElementById('btn-prev');
  var btnNext = document.getElementById('btn-next');
  var pills   = document.querySelectorAll('.cat-pill');
  select.value = window.AppState.year;

  select.addEventListener('change', function() {
    setState({ year: this.value });
    _refreshYearButtons(this.value);
  });

  btnPrev.addEventListener('click', function() {
    var y = parseInt(select.value) - 1;
    if (y < 2007) return;
    select.value = String(y);
    setState({ year: select.value });
    _refreshYearButtons(select.value);
  });

  btnNext.addEventListener('click', function() {
    var y = parseInt(select.value) + 1;
    if (y > 2019) return;
    select.value = String(y);
    setState({ year: select.value });
    _refreshYearButtons(select.value);
  });

  pills.forEach(function(pill) {
    pill.addEventListener('click', function() {
      pills.forEach(function(p) { p.classList.remove('active'); });
      pill.classList.add('active');
      setState({ category: pill.dataset.cat });
    });
  });

  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowLeft') {
      btnPrev.click();
    } else if (e.key === 'ArrowRight') {
      btnNext.click();
    }
  });

  _refreshYearButtons(window.AppState.year);
  _updateStats(window.AppState.year, window.AppState.category, data);
}

function _refreshYearButtons(year) {
  document.getElementById('btn-prev').disabled = (parseInt(year) <= 2007);
  document.getElementById('btn-next').disabled = (parseInt(year) >= 2019);
}

function _updateStats(year, category, data) {
  if (!data || !data.stats) return;

  var s = (data.stats[category] || {})[year];
  if (!s) return;

  document.getElementById('stat-total').textContent =
    s.total.toLocaleString();

  var changeEl = document.getElementById('stat-change');
  if (s.pct_change === null || s.pct_change === undefined) {
    changeEl.textContent = '—';
    changeEl.className = '';
  } else {
    var sign = s.pct_change >= 0 ? '+' : '';
    changeEl.textContent = sign + s.pct_change.toFixed(1) + '%';
    changeEl.className   = s.pct_change >= 0 ? 'change-up' : 'change-down';
  }
  document.getElementById('stat-peak').textContent = s.peak_city || '—';
}

window.initControls = initControls;
