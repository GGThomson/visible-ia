// Schema.org JSON-LD of a site for the panel's "copy" button (C8-T04). Mirror of
// src/visible_ia/jsonld.py: a test checks both build exactly the same object.
function instagramUrl(value) {
  if (!value) return null;
  value = value.trim();
  if (value.indexOf("http") === 0) return value;
  return "https://www.instagram.com/" + value.replace(/^@/, "").replace(/^\/+|\/+$/g, "") + "/";
}

function buildJsonLd(c) {
  var type = { IMP: "Dentist", EDE: "Dentist", MES: "MedicalClinic", DER: "MedicalClinic" }[c.category] || "MedicalClinic";
  var specialty = { DER: "Dermatology" }[c.category];
  var address = { "@type": "PostalAddress" };
  if (c.address) address.streetAddress = c.address;
  address.addressLocality = c.district;
  address.addressRegion = "Lima";
  address.addressCountry = "PE";
  var data = { "@context": "https://schema.org", "@type": type, name: c.name, address: address };
  if (specialty) data.medicalSpecialty = specialty;
  if (c.website) data.url = c.website;
  if (c.phone) data.telephone = c.phone;
  if (c.openingHours && c.openingHours.length) data.openingHours = c.openingHours;
  if (c.mapsUrl) data.hasMap = c.mapsUrl;
  var sameAs = [c.mapsUrl, instagramUrl(c.instagram)].concat(c.extraSameAs || []).filter(Boolean);
  sameAs = sameAs.filter(function (u, i) { return sameAs.indexOf(u) === i; });
  if (sameAs.length) data.sameAs = sameAs;
  return data;
}

function jsonLdScript(data) {
  return '<script type="application/ld+json">\n' + JSON.stringify(data, null, 2) + "\n</script>";
}
