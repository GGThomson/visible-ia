// Clinic panel (C7-T04, HU-20): its index with the range and the ADR-003 change, the market
// ranking, sources, monthly evolution and its checklist. Everything is read through RLS:
// the page only asks; migration 0006 decides what this user may see.
(function () {
  "use strict";

  var TREATMENT = { IMP: "Implantes dentales", EDE: "Estética dental", MES: "Medicina estética", DER: "Dermatología" };
  var MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "setiembre", "octubre", "noviembre", "diciembre"];
  var TYPES = { google_profile: "Ficha de Google", doctoralia: "Doctoralia", own_website: "Web propia", social: "Redes sociales", directory: "Directorios y rankings", press: "Prensa", other: "Otras" };
  var TASKS = {
    ficha_google: "Completar tu ficha de Google (categorías, servicios, fotos)",
    resenas: "Pedir reseñas que mencionen el tratamiento y el distrito",
    doctoralia: "Completar tu perfil de Doctoralia",
    web_schema: "Página del tratamiento en tu web, con schema de clínica",
    redes: "Actualizar tus redes con el tratamiento y el distrito",
    bing_places: "Registrar tu clínica en Bing Places"
  };

  var client = panelClient();
  var $ = function (id) { return document.getElementById(id); };

  function el(tag, text, cls) {
    var node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = text;
    if (cls) node.className = cls;
    return node;
  }
  function pct(v) { return v === null || v === undefined ? "—" : Math.round(Number(v)) + " %"; }
  function monthText(iso) { var d = iso.split("-"); return MONTHS[Number(d[1]) - 1] + " de " + d[0]; }
  function changeText(row) {
    var detect = row.detectable_diff ? " (con estos datos, un cambio menor a " + Math.round(row.detectable_diff) + " puntos no se distingue del azar)" : "";
    return {
      up: "Subió frente al mes anterior.",
      down: "Bajó frente al mes anterior.",
      no_clear_change: "Sin cambio claro frente al mes anterior" + detect + ".",
      first_month: "Primer mes medido: desde el próximo verás si sube o baja."
    }[row.change] || "";
  }
  function fail(message) {
    $("cargando").hidden = true;
    $("error").textContent = message;
    $("error").hidden = false;
  }
  async function query(builder) {
    var result = await builder;
    if (result.error) throw result.error;
    return result.data;
  }

  async function renderSite(site, clinics, markets) {
    var market = markets[site.market_id];
    $("titulo").textContent = clinics[site.clinic_id] || "Tu clínica";
    var ranking = await query(client.from("v_panel_ranking").select("*").eq("market_id", site.market_id).order("month", { ascending: false }));
    if (!ranking.length) {
      $("subtitulo").textContent = (market ? TREATMENT[market.category_code] + " en " + market.district : "") + " · todavía no hay mediciones.";
      return;
    }
    var month = ranking[0].month;
    var current = ranking.filter(function (r) { return r.month === month; })
      .sort(function (a, b) { return Number(b.combined) - Number(a.combined); });
    var mine = current.find(function (r) { return r.clinic_id === site.clinic_id; });
    $("subtitulo").textContent = (market ? TREATMENT[market.category_code] + " en " + market.district + " · " : "") + monthText(month);

    $("combinado").textContent = pct(mine && mine.combined);
    $("rango").textContent = mine ? "Entre " + pct(mine.ci_low) + " y " + pct(mine.ci_high) + " de las respuestas." : "";
    $("cambio").textContent = mine ? changeText(mine) : "";
    $("chatgpt").textContent = pct(mine && mine.chatgpt);
    $("google").textContent = pct(mine && mine.google);

    var box = $("ranking");
    box.replaceChildren();
    current.slice(0, 10).concat(current.slice(10).filter(function (r) { return r.is_mine; })).forEach(function (r, i) {
      var row = el("div", null, "fila-barra" + (r.is_mine ? " mia" : ""));
      row.appendChild(el("div", (current.indexOf(r) + 1) + ". " + r.clinic_name, "nombre"));
      var right = el("div");
      var rail = el("div", null, "riel");
      var fill = el("div", null, "relleno");
      fill.style.width = Math.max(Number(r.combined), 0.5) + "%";
      rail.appendChild(fill);
      right.appendChild(rail);
      right.appendChild(el("div", pct(r.combined) + " (entre " + pct(r.ci_low) + " y " + pct(r.ci_high) + ") · ChatGPT " + pct(r.chatgpt) + " · Google " + pct(r.google), "valor"));
      row.appendChild(right);
      box.appendChild(row);
    });

    var evolution = await query(client.from("v_panel_evolution").select("*").eq("site_id", site.id).eq("surface", "combined").order("month", { ascending: false }));
    var total = (evolution.find(function (e) { return e.month === month; }) || {}).n_responses || 0;
    var sources = await query(client.from("v_panel_sources").select("*").eq("market_id", site.market_id).eq("month", month).neq("source_type", "google_profile").order("answers", { ascending: false }).limit(8));
    var tbody = $("fuentes");
    tbody.replaceChildren();
    sources.forEach(function (s) {
      var tr = el("tr");
      tr.appendChild(el("td", s.domain));
      tr.appendChild(el("td", TYPES[s.source_type] || s.source_type));
      tr.appendChild(el("td", total ? Math.round(100 * s.answers / total) + " %" : "—"));
      tbody.appendChild(tr);
    });

    var evo = $("evolucion");
    evo.replaceChildren();
    evolution.forEach(function (e) {
      var tr = el("tr");
      tr.appendChild(el("td", monthText(e.month)));
      tr.appendChild(el("td", pct(e.presence_index)));
      tr.appendChild(el("td", pct(e.ci_low) + "–" + pct(e.ci_high)));
      tr.appendChild(el("td", pct(e.window3_index)));
      tr.appendChild(el("td", { up: "sube", down: "baja", no_clear_change: "sin cambio claro", first_month: "primer mes" }[e.change] || "—"));
      evo.appendChild(tr);
    });

    // Ordered by priority (migration 0007); falls back to creation order where it is missing.
    var ordered = await client.from("tasks").select("*").eq("site_id", site.id).order("priority").order("id");
    var tasks = ordered.error
      ? await query(client.from("tasks").select("*").eq("site_id", site.id).order("id"))
      : ordered.data;
    var list = $("tareas");
    list.replaceChildren();
    if (!tasks.length) list.appendChild(el("p", "Tu checklist aparecerá con tu primer reporte mensual."));
    tasks.forEach(function (t) {
      var label = el("label");
      var box = el("input");
      box.type = "checkbox";
      box.checked = t.status === "done";
      box.addEventListener("change", async function () {
        box.disabled = true;
        var status = box.checked ? "done" : "pending";
        var result = await client.from("tasks").update({ status: status, updated_at: new Date().toISOString() }).eq("id", t.id).select();
        box.disabled = false;
        if (result.error || !result.data.length) { box.checked = !box.checked; alert("No se pudo guardar. Inténtalo de nuevo."); }
      });
      label.appendChild(box);
      label.appendChild(document.createTextNode(" "));
      label.appendChild(el("strong", t.title || TASKS[t.code] || t.code));
      list.appendChild(label);
      if (t.detail) list.appendChild(el("p", t.detail, "detalle-tarea"));
    });
  }

  async function main() {
    if (!client) return fail("El panel no está disponible en este momento.");
    $("salir").addEventListener("click", async function () { await client.auth.signOut(); window.location.replace("login.html"); });
    var session = (await client.auth.getSession()).data.session;
    if (!session) { window.location.replace("login.html"); return; }
    try {
      var sites = await query(client.from("sites").select("id, clinic_id, market_id").order("id"));
      if (!sites.length) return fail("Tu usuario todavía no tiene una clínica asignada. Escríbenos por WhatsApp.");
      var clinicIds = sites.map(function (s) { return s.clinic_id; });
      var marketIds = sites.map(function (s) { return s.market_id; });
      var clinics = {}; (await query(client.from("clinics").select("id, name").in("id", clinicIds))).forEach(function (c) { clinics[c.id] = c.name; });
      var markets = {}; (await query(client.from("markets").select("id, category_code, district").in("id", marketIds))).forEach(function (m) { markets[m.id] = m; });
      if (sites.length > 1) {
        var select = $("sede");
        sites.forEach(function (s, i) {
          var option = el("option", (clinics[s.clinic_id] || "Sede") + " · " + (markets[s.market_id] ? markets[s.market_id].district : ""));
          option.value = String(i);
          select.appendChild(option);
        });
        select.addEventListener("change", function () { renderSite(sites[Number(select.value)], clinics, markets); });
        $("elegir-sede").hidden = false;
      }
      await renderSite(sites[0], clinics, markets);
      $("cargando").hidden = true;
      $("contenido").hidden = false;
    } catch (e) {
      fail("No pudimos cargar tu panel. Recarga la página en un momento.");
    }
  }

  main();
})();
