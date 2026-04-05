/* Signal Rooms — analytics placeholder wiring (no keys)

Usage (optional): set window.SR_ANALYTICS before loading this script.

Example (Plausible):
  <script>
    window.SR_ANALYTICS = { provider: 'plausible', domain: 'sham00.github.io' };
  </script>
  <script src="../../shared/analytics.js"></script>

Example (Cloudflare Web Analytics):
  <script>
    window.SR_ANALYTICS = {
      provider: 'cloudflare',
      token: 'YOUR_TOKEN'
    };
  </script>
  <script src="../../shared/analytics.js"></script>

If SR_ANALYTICS is not set, this script does nothing.
*/
(function () {
  try {
    var cfg = window.SR_ANALYTICS;
    if (!cfg || !cfg.provider) return;

    function addScript(attrs) {
      var s = document.createElement('script');
      Object.keys(attrs).forEach(function (k) {
        if (k === 'text') return;
        s.setAttribute(k, attrs[k]);
      });
      if (attrs.text) s.text = attrs.text;
      document.head.appendChild(s);
    }

    if (cfg.provider === 'plausible') {
      if (!cfg.domain) return;
      addScript({
        defer: 'defer',
        'data-domain': cfg.domain,
        src: 'https://plausible.io/js/script.js'
      });
      return;
    }

    if (cfg.provider === 'cloudflare') {
      if (!cfg.token) return;
      addScript({
        defer: 'defer',
        src: 'https://static.cloudflareinsights.com/beacon.min.js',
        'data-cf-beacon': JSON.stringify({ token: cfg.token })
      });
      return;
    }

    // Unknown provider → noop
  } catch (e) {
    // Never break page rendering due to analytics wiring
    console.warn('[SR analytics] disabled:', e);
  }
})();
