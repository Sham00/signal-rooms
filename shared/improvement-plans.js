/* Signal Rooms — Improvement Plans modules
   A small shared helper to render a rich "Improvement plans" section consistently across rooms.

   Usage:
     <script src="../../shared/improvement-plans.js"></script>
     <div id="improvement-plans"></div>
     <script>
       SR.renderImprovementPlans('#improvement-plans', { accent: '#22d3ee', plans: [...] })
     </script>
*/

(function () {
  'use strict';

  var root = (typeof window !== 'undefined') ? window : globalThis;
  if (!root.SR) root.SR = {};

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normTag(t) {
    if (!t) return '';
    return String(t).trim();
  }

  function tagHtml(tag, accent) {
    tag = normTag(tag);
    if (!tag) return '';
    return (
      '<span class="sr-imp-tag" style="border-color:' + esc(accent) + '33;color:' + esc(accent) + ';">'
      + esc(tag)
      + '</span>'
    );
  }

  function renderPlanCard(plan, accent) {
    var title = plan.title || 'Untitled';
    var blurb = plan.blurb || '';
    var tags = Array.isArray(plan.tags) ? plan.tags : [];
    var bullets = Array.isArray(plan.bullets) ? plan.bullets : [];
    var metrics = Array.isArray(plan.metrics) ? plan.metrics : [];
    var owners = Array.isArray(plan.owners) ? plan.owners : [];
    var horizon = plan.horizon || '';
    var status = plan.status || '';

    var tagsHtml = tags.map(function (t) { return tagHtml(t, accent); }).join('');

    var metaBits = [];
    if (horizon) metaBits.push('<span class="sr-imp-meta-chip">' + esc(horizon) + '</span>');
    if (status) metaBits.push('<span class="sr-imp-meta-chip" style="border-color:' + esc(accent) + '33;">' + esc(status) + '</span>');
    if (owners.length) metaBits.push('<span class="sr-imp-meta-chip">Owner: ' + esc(owners.join(', ')) + '</span>');

    var bulletsHtml = bullets.length
      ? '<ul class="sr-imp-bullets">' + bullets.map(function (b) {
          return '<li>' + esc(b) + '</li>';
        }).join('') + '</ul>'
      : '';

    var metricsHtml = metrics.length
      ? '<div class="sr-imp-metrics">' + metrics.map(function (m) {
          return '<div class="sr-imp-metric">'
            + '<div class="sr-imp-metric-label">' + esc(m.label || '') + '</div>'
            + '<div class="sr-imp-metric-val">' + esc(m.value || '') + '</div>'
            + '</div>'
            ;
        }).join('') + '</div>'
      : '';

    return (
      '<div class="sr-imp-card">'
        + '<div class="sr-imp-card-top">'
          + '<div>'
            + '<div class="sr-imp-card-title" style="color:' + esc(accent) + ';">' + esc(title) + '</div>'
            + (blurb ? '<div class="sr-imp-card-blurb">' + esc(blurb) + '</div>' : '')
          + '</div>'
          + (tagsHtml ? '<div class="sr-imp-tags">' + tagsHtml + '</div>' : '')
        + '</div>'
        + (metaBits.length ? '<div class="sr-imp-meta">' + metaBits.join('') + '</div>' : '')
        + (metricsHtml || bulletsHtml ? ('<div class="sr-imp-card-body">' + metricsHtml + bulletsHtml + '</div>') : '')
      + '</div>'
    );
  }

  function ensureStyles() {
    if (document.getElementById('sr-improvement-plans-styles')) return;
    var style = document.createElement('style');
    style.id = 'sr-improvement-plans-styles';
    style.textContent = (
      '/* Improvement Plans (shared) */\n'
      + '.sr-imp-wrap{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px;}\n'
      + '.sr-imp-sub{font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#666;line-height:1.6;margin-top:-8px;margin-bottom:14px;}\n'
      + '.sr-imp-grid{display:grid;grid-template-columns:1fr;gap:14px;}\n'
      + '@media(min-width:900px){.sr-imp-grid{grid-template-columns:repeat(2,1fr);}}\n'
      + '.sr-imp-card{background:rgba(0,0,0,0.14);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px 14px 12px;}\n'
      + '.sr-imp-card:hover{border-color:rgba(255,255,255,0.12);}\n'
      + '.sr-imp-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;}\n'
      + '.sr-imp-card-title{font-family:\'JetBrains Mono\',monospace;font-weight:800;letter-spacing:0.04em;font-size:12px;text-transform:uppercase;}\n'
      + '.sr-imp-card-blurb{margin-top:6px;color:#b0b0b8;font-size:13px;line-height:1.55;font-family:Inter,system-ui,-apple-system,sans-serif;}\n'
      + '.sr-imp-tags{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end;}\n'
      + '.sr-imp-tag{display:inline-flex;align-items:center;gap:6px;padding:3px 9px;border-radius:999px;border:1px solid rgba(255,255,255,0.10);font-family:\'JetBrains Mono\',monospace;font-size:10px;letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;background:rgba(255,255,255,0.03);}\n'
      + '.sr-imp-meta{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}\n'
      + '.sr-imp-meta-chip{font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#888;border:1px solid rgba(255,255,255,0.08);border-radius:999px;padding:3px 9px;background:rgba(255,255,255,0.02);}\n'
      + '.sr-imp-card-body{margin-top:12px;display:flex;flex-direction:column;gap:10px;}\n'
      + '.sr-imp-metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;}\n'
      + '.sr-imp-metric{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;padding:10px;}\n'
      + '.sr-imp-metric-label{font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#666;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;}\n'
      + '.sr-imp-metric-val{font-family:\'JetBrains Mono\',monospace;font-size:13px;color:#e5e7eb;font-weight:700;}\n'
      + '.sr-imp-bullets{margin:0;padding-left:18px;color:#b0b0b8;font-size:13px;line-height:1.55;font-family:Inter,system-ui,-apple-system,sans-serif;}\n'
      + '.sr-imp-bullets li{margin:6px 0;}\n'
    );
    document.head.appendChild(style);
  }

  /**
   * Render an Improvement Plans section.
   * @param {string|Element} mount Selector or element
   * @param {object} opts
   * @param {string} opts.accent Hex/rgb accent color
   * @param {string} [opts.title] Default "Improvement plans"
   * @param {string} [opts.subtitle]
   * @param {Array}  opts.plans Array of plan objects
   */
  root.SR.renderImprovementPlans = function (mount, opts) {
    opts = opts || {};
    var el = (typeof mount === 'string') ? document.querySelector(mount) : mount;
    if (!el) return;

    ensureStyles();

    var accent = opts.accent || '#fbbf24';
    var title = opts.title || 'Improvement plans';
    var subtitle = opts.subtitle || 'Tight loops to increase signal quality, speed, and reliability.';
    var plans = Array.isArray(opts.plans) ? opts.plans : [];

    var cards = plans.map(function (p) { return renderPlanCard(p, accent); }).join('');

    el.innerHTML = (
      '<div class="sr-imp-wrap">'
        + '<div class="section-title" style="color:' + esc(accent) + ';">' + esc(title) + '</div>'
        + (subtitle ? '<div class="sr-imp-sub">' + esc(subtitle) + '</div>' : '')
        + '<div class="sr-imp-grid">' + cards + '</div>'
      + '</div>'
    );
  };

})();

