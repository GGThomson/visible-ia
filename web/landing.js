// Landing motion and interaction (docs/marca/DESIGN.md §8). Own code, no libraries.
// Everything plays once, lasts 150–900 ms and never loops. With prefers-reduced-motion (or no
// IntersectionObserver) the final state shows at once: figures, bars, label and images.
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canObserve = "IntersectionObserver" in window;
  var $$ = function (sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); };

  // Header: a thin shadow once the page has scrolled.
  var header = document.querySelector(".encabezado");
  function onScroll() { if (header) header.classList.toggle("con-sombra", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Tabs of "Qué recibes": click, arrows, Home/End; the illustration fades in (250 ms).
  var tabs = $$(".pestanas [role=tab]");

  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      panel.hidden = !on;
      panel.classList.toggle("entrando", on && !reduce);
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () { select(tab, false); });
    tab.addEventListener("keydown", function (e) {
      var next = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 }[e.key];
      if (next === undefined) return;
      e.preventDefault();
      select(tabs[(next + tabs.length) % tabs.length], true);
    });
  });

  // Counters: from 0 to the real figure, once, when seen.
  var counters = $$("[data-contar]");
  function show(el, n) { el.textContent = el.getAttribute("data-formato").replace("{n}", n); }
  function count(el) {
    var to = Number(el.getAttribute("data-contar"));
    var start = null;
    function step(now) {
      if (start === null) start = now;
      var p = Math.min((now - start) / 800, 1);
      show(el, Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }

  var chatSteps = $$(".chat .paso");
  var reveal = $$(".aparece, .barras");
  if (reduce || !canObserve) {
    chatSteps.concat(reveal).forEach(function (el) { el.classList.add("visible"); });
    return;  // counters keep the final figure already written in the HTML
  }

  // Chat: the question, then the answer line by line, then "Tu clínica no aparece".
  var delays = [200, 900, 1300, 1650, 2000, 2700];
  chatSteps.forEach(function (el, i) {
    window.setTimeout(function () { el.classList.add("visible"); }, delays[i] || 2700);
  });

  counters.forEach(function (el) {
    el.setAttribute("aria-label", el.textContent);
    show(el, 0);
  });
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target;
      observer.unobserve(el);
      if (el.hasAttribute("data-contar")) count(el);
      else el.classList.add("visible");
    });
  }, { threshold: 0.2, rootMargin: "0px 0px -40px 0px" });
  reveal.concat(counters).forEach(function (el) { observer.observe(el); });
})();
