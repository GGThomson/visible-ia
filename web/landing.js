// Landing motion (docs/marca/DESIGN.md §8): only three animations, 200–600 ms, no loops.
// 1) the example chat plays once; 2) the report bars grow when seen; 3) sections fade in.
// With prefers-reduced-motion (or without IntersectionObserver) everything shows at once.
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var steps = Array.prototype.slice.call(document.querySelectorAll(".chat .paso"));
  var reveal = Array.prototype.slice.call(document.querySelectorAll(".aparece, .barras"));

  function showAll() {
    steps.concat(reveal).forEach(function (el) { el.classList.add("visible"); });
  }
  if (reduce || !("IntersectionObserver" in window)) { showAll(); return; }

  // Chat: the question, then the answer line by line, then "Tu clínica no aparece".
  var delays = [200, 900, 1300, 1650, 2000, 2700];
  steps.forEach(function (el, i) {
    window.setTimeout(function () { el.classList.add("visible"); }, delays[i] || 2700);
  });

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
  reveal.forEach(function (el) { observer.observe(el); });
})();
