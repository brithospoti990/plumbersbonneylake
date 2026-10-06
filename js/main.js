/* plumbersbonneylake.com — navigation + lead form */
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var navWrap = document.querySelector('.nav-wrap');
  var isDesktop = function () { return window.matchMedia('(min-width: 901px)').matches; };

  if (toggle && navWrap) {
    toggle.addEventListener('click', function () {
      var open = navWrap.getAttribute('data-open') === 'true';
      navWrap.setAttribute('data-open', open ? 'false' : 'true');
      toggle.setAttribute('aria-expanded', open ? 'false' : 'true');
    });
  }

  var dropBtns = document.querySelectorAll('.nav button[aria-controls]');
  function closeAll(except) {
    dropBtns.forEach(function (b) {
      if (b === except) return;
      b.setAttribute('aria-expanded', 'false');
      var m = document.getElementById(b.getAttribute('aria-controls'));
      if (m) m.setAttribute('data-open', 'false');
    });
  }
  dropBtns.forEach(function (btn) {
    var menu = document.getElementById(btn.getAttribute('aria-controls'));
    if (!menu) return;
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      closeAll(btn);
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      menu.setAttribute('data-open', open ? 'false' : 'true');
    });
    var li = btn.parentNode, timer;
    li.addEventListener('mouseenter', function () {
      if (!isDesktop()) return;
      clearTimeout(timer); closeAll(btn);
      btn.setAttribute('aria-expanded', 'true'); menu.setAttribute('data-open', 'true');
    });
    li.addEventListener('mouseleave', function () {
      if (!isDesktop()) return;
      timer = setTimeout(function () {
        btn.setAttribute('aria-expanded', 'false'); menu.setAttribute('data-open', 'false');
      }, 180);
    });
  });
  document.addEventListener('click', function (e) {
    if (header && !header.contains(e.target)) closeAll();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeAll(); if (navWrap) navWrap.setAttribute('data-open', 'false'); }
  });

  /* Lead form → /api/lead (Vercel serverless → Upstash KV) */
  var form = document.getElementById('lead-form');
  if (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.querySelector('[name="website"]').value) return; // honeypot
      var data = {};
      new FormData(form).forEach(function (v, k) { data[k] = v; });
      data.page = location.pathname;
      status.className = 'form-status'; status.textContent = 'Sending…';
      var btn = form.querySelector('button[type="submit"]'); btn.disabled = true;
      fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error('bad'); return r.json(); })
        .then(function () {
          status.className = 'form-status ok';
          status.textContent = 'Request received. Ashino or a team member will call you shortly. For an emergency, call (253) 465-7734 now.';
          form.reset();
        })
        .catch(function () {
          status.className = 'form-status err';
          status.textContent = 'The form could not be sent. Please call (253) 465-7734 and we will take care of you right away.';
        })
        .finally(function () { btn.disabled = false; });
    });
  }
})();
