/* Signal Rooms — persistent navigation bar
   Drop <script src="../../shared/nav.js"></script> (or ./shared/nav.js from hub)
   at the very top of <body> in any room page. */
(function () {
  var path = window.location.pathname;

  // Detect depth: are we inside /rooms/<name>/ ?
  var inRoom = /\/rooms\/[^/]+\/?/.test(path);
  var base   = inRoom ? '../../' : './';

  // Load shell.css if not already present
  if (!document.getElementById('sr-shell-css')) {
    var lnk = document.createElement('link');
    lnk.id   = 'sr-shell-css';
    lnk.rel  = 'stylesheet';
    lnk.href = base + 'shared/shell.css';
    document.head.appendChild(lnk);
  }

  var rooms = [
    { name: '🟡 Gold',    href: base + 'rooms/gold/',     match: '/rooms/gold',    live: true  },
    { name: '🧠 GPU',     href: base + 'rooms/gpu/',      match: '/rooms/gpu',     live: true  },
    { name: '🛢️ Oil',     href: base + 'rooms/oil-gas/',  match: '/rooms/oil-gas', live: true },
    { name: '🏠 Housing', href: base + 'rooms/housing/',  match: '/rooms/housing', live: false },
  ];

  var roomLinks = rooms.map(function (r) {
    var cls = 'sr-room-link';
    if (path.indexOf(r.match) !== -1) cls += ' active';
    if (!r.live) cls += ' stub';
    return '<a class="' + cls + '" href="' + r.href + '">' + r.name + '</a>';
  }).join('');

  var nav = document.createElement('nav');
  nav.id = 'sr-nav';
  nav.setAttribute('role', 'navigation');
  nav.setAttribute('aria-label', 'Signal Rooms navigation');
  nav.innerHTML =
    '<a class="sr-brand" href="' + base + '">' +
      '<span class="sr-logo" aria-hidden="true"></span>' +
      'Signal Rooms' +
    '</a>' +
    '<div class="sr-rooms">' + roomLinks + '</div>';

  // Insert as very first child of body so it renders before anything else
  var body = document.body;
  if (body.firstChild) {
    body.insertBefore(nav, body.firstChild);
  } else {
    body.appendChild(nav);
  }
})();
