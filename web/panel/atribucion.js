// Attribution kit of the panel (C9-T02). Mirror of src/visible_ia/atribucion.py: a test checks
// both build the same links and coupon.
var INTAKE_QUESTION = "¿Cómo nos conociste?";
var INTAKE_OPTIONS = [
  "Google o Google Maps",
  "ChatGPT u otra IA (Gemini, Copilot…)",
  "Instagram, Facebook o TikTok",
  "Doctoralia",
  "Recomendación de un amigo o familiar",
  "Otro"
];
var PLACEMENTS = [
  ["Ficha de Google (botón «Sitio web»)", "google", "organic", "ficha-google"],
  ["Perfil de Doctoralia (enlace a tu web)", "doctoralia", "referral", "perfil"],
  ["Bio de Instagram", "instagram", "social", "bio"]
];
var GENERIC_WORDS = ["clinica", "clinicas", "centro", "consultorio", "dental", "dentales", "odontologica",
  "odontologico", "odontologia", "estetica", "medica", "medico", "dermatologia", "dr", "dra",
  "de", "del", "la", "las", "el", "los", "y", "en", "sede", "spa"];

function taggedUrl(website, source, medium, campaign) {
  var value = (website || "").trim();
  if (!value) return null;
  if (!/^https?:\/\//i.test(value)) value = "https://" + value;
  var url;
  try { url = new URL(value); } catch (e) { return null; }
  if (url.hostname.indexOf(".") === -1) return null;
  var keep = [];
  url.searchParams.forEach(function (v, k) { if (k.indexOf("utm_") !== 0) keep.push([k, v]); });
  keep.push(["utm_source", source], ["utm_medium", medium], ["utm_campaign", campaign]);
  url.search = new URLSearchParams(keep).toString();
  return url.toString();
}

function utmLinks(website) {
  return PLACEMENTS.map(function (p) {
    return { placement: p[0], url: taggedUrl(website, p[1], p[2], p[3]) };
  }).filter(function (l) { return l.url; });
}

function suggestedCoupon(clinicName) {
  var plain = clinicName.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
  var words = plain.split(/[^A-Z0-9]+/).filter(Boolean);
  var word = words.find(function (w) { return GENERIC_WORDS.indexOf(w.toLowerCase()) === -1 && w.length > 1; });
  return "IA-" + (word || "VISIBLE").slice(0, 14);
}
