"""Compare Gemini API answers (registro-api.csv) with the manual sample (registro.csv).

Clinic lists per question/surface were extracted by hand from the sample on 2026-09-26.
Each clinic is a list of aliases; a match is a case/accent-insensitive substring hit.
"""
import csv
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_CSV = ROOT / "docs" / "01-descubrimiento" / "prueba-fuentes" / "registro-api.csv"

C = {  # canonical name -> aliases
    "Smiles Peru": ["smiles peru", "smiles perú"], "Perez Yance": ["perez yance", "pérez yance", "americadent"],
    "Velarde-Alvarez": ["velarde"], "Odontologists / Teixeira": ["odontologists", "teixeira"],
    "Elisseum": ["elisseum"], "Krebs": ["krebs"], "Dentum": ["dentum"], "Clínica de Encías": ["clínica de encías", "clinica de encias"],
    "Dr. Rafael Vilchez": ["vilchez"], "Dr. Aldo (implantes)": ["dr. aldo |", "dr. aldo implantes"], "Neodentis": ["neodentis"],
    "Top Smile": ["top smile", "topsmile"], "Amorisa": ["amorisa"], "Karla Leyva": ["karla leyva"],
    "Daniela Francesqui": ["francesqui"], "Raquel Guerra": ["raquel guerra"], "SINNA": ["sinna"], "Romy Flores": ["romy flores"],
    "CERDENT": ["cerdent"], "OdontoFlores": ["odontoflores"],
    "Sonrisa Segura": ["sonrisa segura"], "Luis Pachas": ["pachas"], "Alinea Ortodoncia": ["alinea"],
    "Dental Inn": ["dental inn"], "IDent": ["ident centro dental", "ident surco"], "Dentalindo": ["dentalindo"], "Vilela": ["vilela"],
    "Clínica Dental Alemana": ["dental alemana"],
    "Violeta Muñoz": ["violeta muñoz", "violeta munoz"], "Cuidamedic": ["cuidamedic"], "Elyzea": ["elyzea"],
    "DermaGold": ["dermagold"], "Lady Segovia": ["lady segovia"], "Skinplus": ["skinplus"], "OH! Skin Medic": ["oh! skin", "oh skin"],
    "Saint Paul": ["saint paul"], "Zegarra": ["zegarra"], "Infinity Clinic": ["infinity clinic"], "Medi Esthetic": ["medi esthetic", "mediesthetic"],
    "Piel Bella": ["piel bella", "pielbella"], "IME": ["ime institute", "ime aesthetic"], "Lima Derma": ["lima derma", "limaderma"],
    "Clínica del Mar": ["clínica del mar", "clinica del mar"], "DermaLine Medic": ["dermaline"],
    "Nova Estética": ["nova estética", "nova estetica"], "Aquamed": ["aquamed"], "Calma Estética": ["calma est"],
    "Ciudad Belleza": ["ciudad belleza"], "Clínica Internacional": ["clínica internacional", "clinica internacional"],
    "Dfemme": ["dfemme"], "Plus D'Stethic": ["d'stethic", "dstethic"], "Nanda Skin": ["nanda skin"],
    "Good Hope": ["good hope"], "Skinisima": ["skinisima"], "Dermaos": ["dermaos"], "Dermaperu": ["dermaperu", "dermaperú"],
    "Iderma Capilar": ["iderma"], "Huillca / Skin Experts": ["huillca", "skin experts"], "Dermany / Jenny Vargas": ["dermany", "jenny vargas"],
    "SKINCENTER": ["skincenter", "skin center"],
    "Clínica de la Piel": ["clínica de la piel", "clinica de la piel"], "Phiderm / Valdivia": ["phiderm", "valdivia"],
    "Ricardo Palma": ["ricardo palma"], "Dermasanmartin": ["dermasanmartin"],
    "Azcárate Capilar": ["azcárate", "azcarate"], "Cderma": ["cderma"], "Tempo Skin": ["tempo skin"],
    "Dennisse Arroyo": ["dennisse arroyo"], "Amanda Rivera": ["amanda rivera"], "Aldo Gálvez": ["gálvez canseco", "galvez canseco", "aldo gálvez", "aldo galvez"],
    "Dermática": ["dermática", "dermatica"], "Saravia": ["saravia"], "García Mojonero": ["mojonero"],
    "Olenka Tauma": ["olenka", "tauma"], "Dermolaser": ["dermolaser"],
}

SAMPLE = {  # question -> surface -> clinics named in the manual sample
    "Q01": {"gemini": ["Smiles Peru", "Perez Yance", "Velarde-Alvarez"],
            "google": ["Odontologists / Teixeira", "Smiles Peru", "Perez Yance", "Elisseum"],
            "chatgpt": ["Smiles Peru", "Odontologists / Teixeira"]},
    "Q05": {"gemini": ["Smiles Peru", "Perez Yance"], "google": ["Smiles Peru", "Perez Yance", "Krebs", "Dentum"],
            "chatgpt": ["Clínica de Encías", "Dr. Rafael Vilchez", "Dr. Aldo (implantes)", "Neodentis"]},
    "Q10": {"gemini": ["Top Smile", "Amorisa", "Karla Leyva", "Daniela Francesqui", "Raquel Guerra"],
            "google": ["Amorisa", "SINNA", "Top Smile", "Karla Leyva", "Romy Flores"],
            "chatgpt": ["Daniela Francesqui", "Top Smile", "CERDENT", "Krebs", "OdontoFlores"]},
    "Q11": {"gemini": ["Sonrisa Segura", "Luis Pachas", "Alinea Ortodoncia", "Dental Inn", "IDent"],
            "google": ["Alinea Ortodoncia", "Dentalindo", "Vilela"], "chatgpt": ["Sonrisa Segura", "Clínica Dental Alemana"]},
    "Q16": {"gemini": ["Violeta Muñoz", "Cuidamedic", "Elyzea", "DermaGold"],
            "google": ["Lady Segovia", "Violeta Muñoz", "Cuidamedic"],
            "chatgpt": ["Skinplus", "OH! Skin Medic", "Elyzea", "Cuidamedic"]},
    "Q19": {"gemini": ["Saint Paul", "Zegarra", "Infinity Clinic"], "google": ["Medi Esthetic", "Cuidamedic", "Piel Bella", "Zegarra"],
            "chatgpt": ["IME", "Lima Derma", "Clínica del Mar", "DermaLine Medic"]},
    "Q22": {"gemini": ["Medi Esthetic", "Nova Estética", "Aquamed", "Calma Estética", "Ciudad Belleza"],
            "google": ["Clínica Internacional", "Medi Esthetic", "Ciudad Belleza"],
            "chatgpt": ["Medi Esthetic", "Dfemme", "Plus D'Stethic", "Nanda Skin", "Calma Estética"]},
    "Q24": {"gemini": ["Good Hope", "Lima Derma", "Skinisima"],
            "google": ["Lima Derma", "Dermaos", "Dermaperu", "Iderma Capilar", "Huillca / Skin Experts", "Dermany / Jenny Vargas"],
            "chatgpt": ["Lima Derma", "Dermaperu", "SKINCENTER", "Huillca / Skin Experts"]},
    "Q29": {"gemini": ["Clínica de la Piel"], "google": ["Clínica de la Piel", "Phiderm / Valdivia", "Ricardo Palma", "Clínica Internacional"],
            "chatgpt": ["Clínica de la Piel", "Phiderm / Valdivia", "Dermasanmartin"]},
    "Q30": {"gemini": ["Azcárate Capilar", "Cderma", "Tempo Skin", "Dennisse Arroyo", "Amanda Rivera"],
            "google": ["Aldo Gálvez", "Cderma", "Dermática", "Saravia", "García Mojonero"],
            "chatgpt": ["Olenka Tauma", "Dermolaser", "Cderma"]},
}
LEADER = {"Q01": "Smiles Peru", "Q10": "Top Smile", "Q16": "Cuidamedic", "Q22": "Medi Esthetic",
          "Q24": "Lima Derma", "Q29": "Clínica de la Piel", "Q30": "Cderma"}


def norm(s):
    return unicodedata.normalize("NFC", s.lower())


def found(text):
    t = norm(text)
    return {name for name, aliases in C.items()
            if any(re.search(r"(?<!\w)" + re.escape(norm(a).strip()) + r"(?!\w)", t) for a in aliases)}


def main():
    rows = list(csv.DictReader(open(API_CSV, encoding="utf-8", newline="")))
    by = defaultdict(list)
    for r in rows:
        by[(r["config"], r["pregunta_id"])].append(r)
    for cfg in sorted({r["config"] for r in rows}):
        print(f"\n=== Config {cfg} ===")
        tot = {"q_all_named": 0, "q_share_gemini": 0, "q_share_any": 0, "leader_hit": 0}
        for q in SAMPLE:
            rs = by.get((cfg, q), [])
            per_rep = [found(r["respuesta"] + " " + r["lugares_maps"]) for r in rs]
            union = set().union(*per_rep) if per_rep else set()
            named = sum(1 for r in rs if r["respuesta"].strip() and (r["lugares_maps"] or "**" in r["respuesta"]))
            app = set(SAMPLE[q]["gemini"])
            any_surface = set().union(*SAMPLE[q].values())
            inter_all = set.intersection(*per_rep) if len(per_rep) == 3 else set()
            print(f"{q}: reps={len(rs)} con-lista={named} | vs app Gemini {len(union & app)}/{len(app)} "
                  f"{sorted(union & app)} | vs cualquier superficie {len(union & any_surface)} "
                  f"| en las 3 reps {sorted(inter_all)} | líder {LEADER.get(q, '-')}: "
                  f"{'sí' if LEADER.get(q) in union else ('no' if q in LEADER else '-')}")
            tot["q_all_named"] += named == len(rs) and len(rs) > 0
            tot["q_share_gemini"] += bool(union & app)
            tot["q_share_any"] += bool(union & any_surface)
            tot["leader_hit"] += LEADER.get(q) in union
        print("Totales:", tot)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
