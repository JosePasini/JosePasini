/* =========================================================================
   Jose Pasini - a text adventure.
   Vanilla JS, no build step. Every user facing string comes from story.json;
   this file only decides where each one goes.
   ========================================================================= */

(function () {
  'use strict';

  var LANG_KEY = 'jp.lang';
  var DEFAULT_LANG = 'en';

  /* Which stop of the journey map each chapter sits on. */
  var MAP_STOP = {
    mendoza: 0, utn: 0, challenge: 0,
    escala: 1,
    avion: 2, idioma: 2, dublin: 2,
    hoy: 3
  };

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  var data = null;
  var lang = DEFAULT_LANG;
  var screens = [];          // [intro, ...chapters, end]
  var index = 0;
  var opened = {};           // project id -> true, kept across language swaps

  var el = {
    stage: document.getElementById('stage'),
    brand: document.getElementById('brand'),
    langToggle: document.getElementById('lang-toggle'),
    menuOpen: document.getElementById('menu-open'),
    boringOpen: document.getElementById('boring-open'),
    progressLabel: document.getElementById('progress-label'),
    progressCounter: document.getElementById('progress-counter'),
    progressBar: document.getElementById('progress-bar'),
    progressFill: document.getElementById('progress-fill'),
    mapLabel: document.getElementById('map-label'),
    map: document.getElementById('map'),
    prev: document.getElementById('nav-prev'),
    next: document.getElementById('nav-next'),
    menuDialog: document.getElementById('menu-dialog'),
    menuTitle: document.getElementById('menu-title'),
    menuList: document.getElementById('menu-list'),
    boringDialog: document.getElementById('boring-dialog'),
    boringTitle: document.getElementById('boring-title'),
    boringSummary: document.getElementById('boring-summary'),
    boringStack: document.getElementById('boring-stack'),
    boringLinks: document.getElementById('boring-links')
  };

  var announcer = document.createElement('div');
  announcer.className = 'visually-hidden';
  announcer.setAttribute('aria-live', 'polite');
  document.body.appendChild(announcer);

  /* ------------------------------------------------------------ helpers */

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* The only markup story.json uses is **bold** and `code`. Nothing else. */
  function md(s) {
    return esc(s)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  }

  function t(obj) {
    if (!obj) return '';
    return typeof obj === 'string' ? obj : (obj[lang] != null ? obj[lang] : obj[DEFAULT_LANG]);
  }

  function ui(key) { return t(data.ui[key]); }

  function artFigure(base, alt) {
    if (!base) return '';
    return '<figure class="art" data-failed="false">' +
      '<img class="art__img" src="assets/' + esc(lang) + '/' + esc(base) + '.svg" ' +
      'alt="' + esc(alt || '') + '" width="880" height="210" decoding="async">' +
      '</figure>';
  }

  /* A panel that never arrived should not leave a hole in the page. */
  function wireArt(root) {
    var imgs = root.querySelectorAll('.art__img');
    for (var i = 0; i < imgs.length; i++) {
      (function (img) {
        var fail = function () { img.parentNode.setAttribute('data-failed', 'true'); };
        img.addEventListener('error', fail);
        if (img.complete && img.naturalWidth === 0) fail();
      })(imgs[i]);
    }
  }

  function paragraphs(list) {
    if (!list || !list.length) return '';
    return '<div class="prose">' + list.map(function (p) {
      return '<p>' + md(p) + '</p>';
    }).join('') + '</div>';
  }

  function stackList(stack) {
    if (!stack || !stack.length) return '';
    return '<ul class="stack">' + stack.map(function (s) {
      return '<li>' + esc(s) + '</li>';
    }).join('') + '</ul>';
  }

  /* ------------------------------------------------------------ screens */

  function visible(list) {
    return (list || []).filter(function (item) { return !item.hidden; });
  }

  function buildScreens() {
    screens = [{ kind: 'intro' }];
    visible(data.chapters).forEach(function (ch) { screens.push({ kind: 'chapter', ch: ch }); });
    screens.push({ kind: 'end' });
  }

  function renderIntro() {
    var a = data.standalone_art.title;
    var alt = t(a) ? (t(a).name || '') : '';
    return '<section class="screen intro">' +
      artFigure('title', alt) +
      '<p class="intro__hook">' + md(t(data.intro.hook)) + '</p>' +
      '<p class="intro__body">' + md(t(data.intro.body)) + '</p>' +
      '<button class="btn btn--big" data-action="play" type="button">' +
        esc(ui('start')) + '</button>' +
      '</section>';
  }

  function renderProject(id) {
    var p = data.projects[id];
    if (!p || p.hidden) return '';
    var name = t(p.name);
    var bodyId = 'reveal-' + id;
    var isOpen = !!opened[id];
    var linkLabel = p.url_kind === 'live' ? ui('live') : ui('open_code');

    var reveal =
      '<div class="reveal" id="' + bodyId + '">' +
        '<div class="reveal__inner"><div class="reveal__pad">' +
          artFigure(p.art, name) +
          paragraphs(t(p.body)) +
          stackList(p.stack) +
          (p.url ? '<a class="project__link" href="' + esc(p.url) + '" target="_blank" rel="noopener noreferrer">' +
            esc(linkLabel) + '</a>' : '') +
        '</div></div>' +
      '</div>';

    /* An egg is not a card: it sits in the margin, dim, and lights up when
       you get near it. */
    if (p.is_egg) {
      return '<div class="egg' + (isOpen ? ' is-open' : '') + '" data-project="' + esc(id) + '">' +
        '<button class="egg__toggle" type="button" data-toggle="' + esc(id) + '" ' +
          'aria-expanded="' + isOpen + '" aria-controls="' + bodyId + '">' +
          '<span class="egg__mark" aria-hidden="true">*</span>' +
          '<span class="egg__name">' + esc(name) + '</span>' +
          '<span class="egg__tagline">' + esc(t(p.tagline)) + '</span>' +
        '</button>' + reveal +
        '</div>';
    }

    return '<article class="project' + (isOpen ? ' is-open' : '') + '" data-project="' + esc(id) + '">' +
      '<h3 class="project__head">' +
        '<button class="project__toggle" type="button" data-toggle="' + esc(id) + '" ' +
          'aria-expanded="' + isOpen + '" aria-controls="' + bodyId + '">' +
          '<span class="project__eyebrow">' + esc(ui('project')) + '</span>' +
          '<span class="project__name">' + esc(name) + '</span>' +
          '<span class="project__tagline">' + esc(t(p.tagline)) + '</span>' +
          '<span class="project__mark" aria-hidden="true">+</span>' +
        '</button>' +
      '</h3>' + reveal +
      '</article>';
  }

  function renderTable(table) {
    var head = t(table.head);
    var rows = table.rows.map(function (r) {
      return '<tr>' +
        '<td data-label="' + esc(head[0]) + '"><a href="' + esc(r[1]) + '" target="_blank" rel="noopener noreferrer">' + esc(r[0]) + '</a></td>' +
        '<td data-label="' + esc(head[1]) + '">' + esc(t(r[2])) + '</td>' +
        '<td class="ctable__stack" data-label="' + esc(head[2]) + '">' + esc(r[3]) + '</td>' +
        '</tr>';
    }).join('');

    return '<div class="table-wrap"><table class="ctable"><thead><tr>' +
      head.map(function (h) { return '<th scope="col">' + esc(h) + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  function renderChapter(ch) {
    var eggs = [];
    var normal = [];
    (ch.projects || []).forEach(function (id) {
      var p = data.projects[id];
      if (p && p.is_egg) eggs.push(id); else normal.push(id);
    });

    return '<section class="screen chapter">' +
      '<p class="eyebrow">' + esc(ui('chapter')) + ' ' + esc(ch.num) + '</p>' +
      '<h2 class="chapter__title">' + esc(t(ch.title)) + '</h2>' +
      '<p class="chapter__tagline">' + esc(t(ch.tagline)) + '</p>' +
      artFigure(ch.art, t(ch.title)) +
      paragraphs(t(ch.body)) +
      (ch.table ? renderTable(ch.table) : '') +
      (normal.length ? '<div class="projects">' + normal.map(renderProject).join('') + '</div>' : '') +
      eggs.map(renderProject).join('') +
      '</section>';
  }

  function renderEnd() {
    return '<section class="screen end">' +
      artFigure('final', t(data.standalone_art.final).done || '') +
      '<p class="end__outro">' + md(ui('outro')) + '</p>' +
      linksList() +
      '<button class="btn btn--big" data-action="restart" type="button">' + esc(ui('restart')) + '</button>' +
      '</section>';
  }

  var LINK_ICONS = {
    linkedin: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5C4.98 4.88 3.88 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.24 8.25h4.52V24H.24V8.25zM8.34 8.25h4.33v2.14h.06c.6-1.14 2.08-2.34 4.28-2.34 4.58 0 5.43 3.01 5.43 6.93V24h-4.52v-7.79c0-1.86-.03-4.25-2.59-4.25-2.59 0-2.99 2.02-2.99 4.11V24H8.34V8.25z"/></svg>',
    email: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M2 5.5A2.5 2.5 0 0 1 4.5 3h15A2.5 2.5 0 0 1 22 5.5v13a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 18.5v-13zm2.4.5 7.6 5.2L19.6 6H4.4zm15.1 1.7-6.8 4.66a2 2 0 0 1-2.2 0L3.5 7.7V18.5c0 .28.22.5.5.5h16a.5.5 0 0 0 .5-.5V7.7z"/></svg>',
    leetcode: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 3.1 7.7 8.9a4.2 4.2 0 0 0 0 6l3.7 3.7 1.4-1.4-3.7-3.7a2.2 2.2 0 0 1 0-3.1l5.8-5.8L13.5 3.1zm2.7 5.2-1.4 1.4 3.2 3.2-3.2 3.2 1.4 1.4 3.9-3.9a2 2 0 0 0 0-2.8l-3.9-3.5zM8.1 12.9 4.8 9.6 3.4 11l3.3 3.3 1.4-1.4z"/></svg>'
  };

  function linksList() {
    var keys = Object.keys(data.links);
    return '<ul class="links">' + keys.map(function (k) {
      var label = (data.link_labels && data.link_labels[k]) || k;
      var icon = LINK_ICONS[k] || '';
      return '<li><a class="link link--' + k + '" href="' + esc(data.links[k]) + '"' +
        (data.links[k].indexOf('mailto:') === 0 ? '' : ' target="_blank" rel="noopener noreferrer"') +
        '>' + icon + '<span>' + esc(label) + '</span></a></li>';
    }).join('') + '</ul>';
  }

  function renderScreen(i) {
    var s = screens[i];
    if (s.kind === 'intro') return renderIntro();
    if (s.kind === 'end') return renderEnd();
    return renderChapter(s.ch);
  }

  /* ---------------------------------------------------------- transition */

  function mount(i, dir) {
    var wrap = document.createElement('div');
    wrap.innerHTML = renderScreen(i);
    var node = wrap.firstElementChild;
    wireArt(node);

    /* Anything still animating out from a previous jump goes now, so there is
       never more than one outgoing screen in the DOM. */
    var stale = el.stage.querySelectorAll('.screen.is-leaving');
    for (var s = 0; s < stale.length; s++) stale[s].remove();

    var old = el.stage.firstElementChild;
    var animate = !reduce.matches && dir !== 'none' && old;

    if (old) {
      if (!animate) {
        old.remove();
      } else {
        old.classList.add('is-leaving');
        old.setAttribute('data-dir', dir);
        old.setAttribute('aria-hidden', 'true');
        old.inert = true;
        var drop = function (e) {
          if (e && e.target !== old) return;
          old.removeEventListener('animationend', drop);
          if (old.parentNode) old.remove();
        };
        old.addEventListener('animationend', drop);
        window.setTimeout(drop, 700);
      }
    }

    if (animate) {
      node.classList.add('is-entering');
      node.setAttribute('data-dir', dir);
      var clean = function (e) {
        if (e.target !== node) return;
        node.removeEventListener('animationend', clean);
        node.classList.remove('is-entering');
      };
      node.addEventListener('animationend', clean);
    }

    el.stage.appendChild(node);
  }

  /* ---------------------------------------------------------------- HUD */

  function buildMap() {
    var m = t(data.standalone_art.mapa);
    el.map.setAttribute('aria-label', ui('the_run'));
    el.map.innerHTML = m.stops.map(function (stop) {
      return '<li class="map__stop" data-state="todo">' +
        '<span class="map__dot" aria-hidden="true"></span>' +
        '<span class="map__text">' +
          '<span class="map__name">' + esc(stop[0]) + '</span>' +
          '<span class="map__year">' + esc(stop[1]) + '</span>' +
        '</span>' +
        '</li>';
    }).join('');
  }

  function currentStop() {
    var s = screens[index];
    if (s.kind === 'intro') return -1;
    if (s.kind === 'end') return 3;
    return MAP_STOP[s.ch.id] != null ? MAP_STOP[s.ch.id] : -1;
  }

  function updateHud() {
    var total = data.chapters.length;
    var s = screens[index];
    var done = s.kind === 'intro' ? 0 : (s.kind === 'end' ? total : s.ch.num);

    el.progressLabel.textContent = ui('progress');
    el.progressCounter.textContent = done + ' / ' + total;
    el.progressFill.style.width = (done / total * 100) + '%';
    el.progressBar.setAttribute('aria-valuenow', String(Math.round(done / total * 100)));
    el.progressBar.setAttribute('aria-label', ui('progress'));

    var here = currentStop();
    var stops = el.map.children;
    for (var i = 0; i < stops.length; i++) {
      var state = here < 0 ? 'todo' : (i < here ? 'done' : (i === here ? 'here' : 'todo'));
      stops[i].setAttribute('data-state', state);
      if (state === 'here') stops[i].setAttribute('aria-current', 'step');
      else stops[i].removeAttribute('aria-current');
    }

    el.prev.disabled = index === 0;
    el.next.disabled = index === screens.length - 1;
  }

  function updateChrome() {
    document.documentElement.lang = lang;
    el.brand.textContent = t(data.standalone_art.title).name;
    el.brand.setAttribute('aria-label', t(data.standalone_art.title).name);
    el.langToggle.textContent = ui('lang_switch');
    el.menuOpen.textContent = ui('menu');
    el.boringOpen.textContent = ui('cv_title');
    el.mapLabel.textContent = ui('the_run');
    el.prev.textContent = ui('prev');
    el.next.textContent = ui('next');
    el.menuTitle.textContent = ui('menu');
    el.boringTitle.textContent = ui('cv_title');

    /* story.json has no "close" label, so the sheet dismiss reuses ui.prev. */
    var closes = document.querySelectorAll('.sheet__close');
    for (var i = 0; i < closes.length; i++) closes[i].setAttribute('aria-label', ui('prev'));
  }

  function buildMenu() {
    el.menuList.innerHTML = screens.map(function (s, i) {
      if (s.kind !== 'chapter') return '';
      var ch = s.ch;
      return '<li><button class="menu-item" type="button" data-go="' + i + '">' +
        '<span class="menu-item__num">' + esc(ch.num) + '</span>' +
        '<span class="menu-item__title">' + esc(t(ch.title)) + '</span>' +
        '<span class="menu-item__tagline">' + esc(t(ch.tagline)) + '</span>' +
        '</button></li>';
    }).join('');
    markMenu();
  }

  function markMenu() {
    var items = el.menuList.querySelectorAll('.menu-item');
    for (var i = 0; i < items.length; i++) {
      if (Number(items[i].getAttribute('data-go')) === index) items[i].setAttribute('aria-current', 'true');
      else items[i].removeAttribute('aria-current');
    }
  }

  function buildBoring() {
    el.boringSummary.innerHTML = md(t(data.boring.summary));
    el.boringStack.innerHTML = data.boring.stack.map(function (row) {
      return '<div><dt>' + esc(t(row[0])) + '</dt><dd>' + esc(row[1]) + '</dd></div>';
    }).join('');
    el.boringLinks.innerHTML = linksList().replace(/^<ul class="links">|<\/ul>$/g, '');
  }

  /* -------------------------------------------------------------- routing */

  function hashFor(i) {
    var s = screens[i];
    if (s.kind === 'intro') return '';
    if (s.kind === 'end') return '#end';
    return '#ch=' + s.ch.id;
  }

  function indexFromHash() {
    var h = decodeURIComponent(String(location.hash).replace(/^#/, ''));
    if (!h || h === 'intro') return 0;
    if (h === 'end') return screens.length - 1;
    var m = /^ch=(.+)$/.exec(h);
    if (m) {
      for (var i = 0; i < data.chapters.length; i++) {
        if (data.chapters[i].id === m[1]) return i + 1;
      }
    }
    return 0;
  }

  var suppressHash = false;

  function go(i, opts) {
    opts = opts || {};
    i = Math.max(0, Math.min(screens.length - 1, i));
    var dir = opts.dir || (i > index ? 'fwd' : (i < index ? 'back' : 'none'));
    if (i === index && !opts.force) return;

    index = i;
    mount(index, dir);
    updateHud();
    markMenu();

    if (!opts.silent) {
      var target = location.pathname + location.search + hashFor(index);
      suppressHash = true;
      if (opts.replace) history.replaceState(null, '', target);
      else history.pushState(null, '', target);
      window.setTimeout(function () { suppressHash = false; }, 0);
    }

    if (!opts.keepScroll) window.scrollTo(0, 0);

    var s = screens[index];
    if (s.kind === 'chapter') announcer.textContent = ui('chapter') + ' ' + s.ch.num + ': ' + t(s.ch.title);
    else announcer.textContent = t(data.standalone_art.title).name;

    if (opts.focusHeading) {
      var head = el.stage.querySelector('.screen h2, .screen .intro__hook, .screen .end__outro');
      if (head) { head.setAttribute('tabindex', '-1'); head.focus({ preventScroll: true }); }
    }
  }

  /* ------------------------------------------------------------ language */

  function setLang(next, opts) {
    opts = opts || {};
    lang = data.langs.indexOf(next) >= 0 ? next : DEFAULT_LANG;
    try { localStorage.setItem(LANG_KEY, lang); } catch (e) { /* private mode */ }

    updateChrome();
    buildMap();
    buildMenu();
    buildBoring();
    updateHud();

    if (!opts.initial) {
      var url = new URL(location.href);
      url.searchParams.set('lang', lang);
      history.replaceState(null, '', url.pathname + url.search + hashFor(index));

      var y = window.scrollY;
      mount(index, 'none');
      window.scrollTo(0, y);
    }
  }

  function initialLang() {
    var q = new URL(location.href).searchParams.get('lang');
    if (q && data.langs.indexOf(q) >= 0) return q;
    try {
      var saved = localStorage.getItem(LANG_KEY);
      if (saved && data.langs.indexOf(saved) >= 0) return saved;
    } catch (e) { /* ignore */ }
    return DEFAULT_LANG;
  }

  /* -------------------------------------------------------------- events */

  function anyDialogOpen() {
    return el.menuDialog.open || el.boringDialog.open;
  }

  function openDialog(dlg) {
    if (anyDialogOpen()) return;
    if (typeof dlg.showModal === 'function') dlg.showModal();
    else dlg.setAttribute('open', '');
    var first = dlg.querySelector('button, a, [tabindex]');
    if (first) first.focus();
  }

  function toggleProject(id, host) {
    var isOpen = host.classList.toggle('is-open');
    opened[id] = isOpen;
    var btn = host.querySelector('[data-toggle]');
    if (btn) btn.setAttribute('aria-expanded', String(isOpen));
  }

  function wireEvents() {
    el.stage.addEventListener('click', function (e) {
      var toggle = e.target.closest('[data-toggle]');
      if (toggle) {
        var host = toggle.closest('[data-project]');
        if (host) toggleProject(host.getAttribute('data-project'), host);
        return;
      }
      var action = e.target.closest('[data-action]');
      if (!action) return;
      if (action.getAttribute('data-action') === 'play') go(1, { dir: 'fwd' });
      if (action.getAttribute('data-action') === 'restart') go(0, { dir: 'back' });
    });

    el.prev.addEventListener('click', function () { go(index - 1, { dir: 'back' }); });
    el.next.addEventListener('click', function () { go(index + 1, { dir: 'fwd' }); });
    el.brand.addEventListener('click', function () { go(0, { dir: 'back' }); });

    el.langToggle.addEventListener('click', function () {
      var i = data.langs.indexOf(lang);
      setLang(data.langs[(i + 1) % data.langs.length]);
    });

    el.menuOpen.addEventListener('click', function () { openDialog(el.menuDialog); });
    el.boringOpen.addEventListener('click', function () { openDialog(el.boringDialog); });

    el.menuList.addEventListener('click', function (e) {
      var item = e.target.closest('[data-go]');
      if (!item) return;
      el.menuDialog.close();
      go(Number(item.getAttribute('data-go')), { focusHeading: true });
    });

    /* Clicking the dim area around a sheet, or its dismiss, closes it. */
    [el.menuDialog, el.boringDialog].forEach(function (dlg) {
      dlg.addEventListener('click', function (e) {
        if (e.target === dlg || e.target.closest('[data-close]')) dlg.close();
      });
    });

    window.addEventListener('hashchange', function () {
      if (suppressHash) return;
      go(indexFromHash(), { silent: true });
    });

    window.addEventListener('popstate', function () {
      go(indexFromHash(), { silent: true });
    });

    document.addEventListener('keydown', function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      var tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) return;

      if (e.key === 'Escape') {
        if (anyDialogOpen()) return;   // the dialog closes itself
        e.preventDefault();
        openDialog(el.menuDialog);
        return;
      }
      if (anyDialogOpen()) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1, { dir: 'fwd' }); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1, { dir: 'back' }); }
    });
  }

  /* ---------------------------------------------------------------- boot */

  function start(json) {
    data = json;
    buildScreens();
    lang = initialLang();
    setLang(lang, { initial: true });
    wireEvents();
    index = -1;                                     // force the first mount
    go(indexFromHash(), { dir: 'none', replace: true, force: true });
  }

  function fail(err) {
    console.error(err);
    el.stage.innerHTML = '<section class="screen panel" style="padding:1.5rem"><p class="mono">' +
      esc(String(err.message || err)) + '</p></section>';
  }

  /* The story is embedded in the page by tools/build_site.py, so this opens
     straight from disk with no server and no request that can fail. */
  var inline = document.getElementById('story-data');
  if (!inline || !inline.textContent.trim()) {
    fail(new Error('story-data is empty -- run: python3 tools/build.py'));
  } else {
    try { start(JSON.parse(inline.textContent)); } catch (e) { fail(e); }
  }
})();
