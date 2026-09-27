// Landing form (C6-T03): inserts a prospect with the public anon key; RLS only allows that.
// config.js is generated at deploy time (web.yml): production -> prod, previews -> dev.
(function () {
  "use strict";

  var UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  var STORE = "visible-ia-utm";

  // Keep the UTM of the first visit of the session, even if the visitor navigates.
  function captureUtm() {
    var params = new URLSearchParams(window.location.search);
    var utm = {};
    UTM_KEYS.forEach(function (k) {
      if (params.get(k)) utm[k] = params.get(k).slice(0, 200);
    });
    try {
      if (Object.keys(utm).length) sessionStorage.setItem(STORE, JSON.stringify(utm));
      var saved = sessionStorage.getItem(STORE);
      if (saved) utm = JSON.parse(saved);
    } catch (e) { /* private mode: use this page's UTM only */ }
    if (document.referrer && !utm.referrer) utm.referrer = document.referrer.slice(0, 200);
    return utm;
  }

  var utm = captureUtm();
  var form = document.getElementById("formulario");
  var button = document.getElementById("enviar");
  var error = document.getElementById("error");
  var done = document.getElementById("resultado");
  var config = window.VISIBLE_IA_CONFIG;

  function fail(message) {
    error.textContent = message;
    error.hidden = false;
    button.removeAttribute("aria-busy");
    button.disabled = false;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    error.hidden = true;
    if (!form.checkValidity()) {
      fail(form.consent.checked ? "Revisa los campos marcados." : "Para enviarte el informe necesitamos tu autorización de contacto.");
      form.reportValidity();
      return;
    }
    // Honeypot: bots fill every field. Pretend it worked and send nothing.
    if (form.website.value) {
      form.hidden = true;
      done.hidden = false;
      return;
    }
    if (!config || !config.supabaseUrl || !config.anonKey) {
      fail("El formulario no está disponible en este momento. Escríbenos por WhatsApp.");
      return;
    }
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    var row = {
      name: form.name.value.trim(),
      clinic_name: form.clinic_name.value.trim(),
      category_code: form.category_code.value,
      district: form.district.value,
      contact: form.contact.value.trim(),
      utm: utm,
      consent: true
    };
    fetch(config.supabaseUrl + "/rest/v1/prospects", {
      method: "POST",
      headers: {
        "apikey": config.anonKey,
        "Authorization": "Bearer " + config.anonKey,
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
      },
      body: JSON.stringify(row)
    }).then(function (response) {
      if (!response.ok) throw new Error(String(response.status));
      form.hidden = true;
      done.hidden = false;
    }).catch(function () {
      fail("No pudimos enviar tu pedido. Inténtalo de nuevo en un momento.");
    });
  });
})();
