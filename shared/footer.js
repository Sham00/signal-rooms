/* Signal Rooms — shared footer
   Drop <script src="../../shared/footer.js"></script> near the end of <body>.
   Works both on the hub (./shared/footer.js) and room pages (../../shared/footer.js).
*/
(function () {
  var path = window.location.pathname;
  var inRoom = /\/rooms\/[^/]+\/?/.test(path);
  var base = inRoom ? '../../' : './';

  // Load shell.css (in case footer used without nav)
  if (!document.getElementById('sr-shell-css')) {
    var lnk = document.createElement('link');
    lnk.id = 'sr-shell-css';
    lnk.rel = 'stylesheet';
    lnk.href = base + 'shared/shell.css';
    document.head.appendChild(lnk);
  }

  // Avoid double-inserting
  if (document.getElementById('sr-footer')) return;

  var year = new Date().getFullYear();

  var foot = document.createElement('footer');
  foot.id = 'sr-footer';
  foot.innerHTML =
    '<div class="sr-footer-wrap">' +
      '<div class="sr-footer-left">© ' + year + ' Signal Rooms</div>' +
      '<div class="sr-footer-right">' +
        '<a href="' + base + '">Hub</a>' +
        '<span class="sr-dot">·</span>' +
        '<a href="https://github.com/Sham00/signal-rooms" target="_blank" rel="noreferrer">GitHub</a>' +
        '<span class="sr-dot">·</span>' +
        '<span class="sr-muted">Static, GitHub Pages friendly</span>' +
      '</div>' +
    '</div>';

  document.body.appendChild(foot);
})();
