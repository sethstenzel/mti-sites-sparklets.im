// Applies the saved site theme before first paint (no flash of the wrong colors).
// Served with a 1-year cache: if you change this file, rename it (v2…) and update index.html.
(function () {
  var themes = { neutral: '#fbf9fa', blush: '#fbf7fb', slate: '#0e1318' };
  var id = null;
  try { id = localStorage.getItem('sparklets.siteTheme'); } catch (e) {}
  if (!themes[id]) id = 'neutral';
  document.documentElement.setAttribute('data-theme', id);
  document.querySelector('meta[name="theme-color"]').setAttribute('content', themes[id]);
})();
