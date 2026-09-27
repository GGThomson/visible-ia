from pathlib import Path

import pytest

from visible_ia.mercados.clinicas import InvalidClinicsFile, parse_clinics_csv, read_clinics_csv

EXAMPLE = Path(__file__).parents[2] / "data" / "ejemplos" / "clinicas-ejemplo.csv"


def test_example_file_parses_cleanly():
    rows, errors = read_clinics_csv(EXAMPLE)
    assert len(rows) == 5 and errors == []
    by_name = {r.name: r for r in rows}
    assert by_name["Centro Ejemplo Tres (Sede Surco)"].review_count == 1020  # "1.020"
    assert by_name["Dra. Ejemplo Cuatro - Dermatóloga"].rating == 4.5  # "4,5"
    assert by_name["Clínica Ejemplo Cinco"].rating is None


def test_semicolon_separator_bom_and_spanish_headers():
    text = "\ufeffNombre;Distrito;Maps_URL;Reseñas;Dirección\nA;Surco;https://m/1;1,100;Av 1\n"
    rows, errors = parse_clinics_csv(text)
    assert errors == []
    assert rows[0].review_count == 1100 and rows[0].address == "Av 1"


def test_bad_rows_are_reported_without_stopping():
    text = (
        "nombre,distrito,maps_url,rating,resenas\n"
        "Buena,Surco,https://m/1,4.7,10\n"
        ",Surco,https://m/2,,\n"
        "Rating malo,Surco,https://m/3,abc,\n"
        "Fuera de rango,Surco,https://m/4,7,\n"
        "Sin http,Surco,maps/5,,\n"
        "Reseñas malas,Surco,https://m/6,,muchas\n"
    )
    rows, errors = parse_clinics_csv(text)
    assert [r.name for r in rows] == ["Buena"]
    assert [e.line for e in errors] == [3, 4, 5, 6, 7]


def test_missing_required_column_fails():
    with pytest.raises(InvalidClinicsFile, match="maps_url"):
        parse_clinics_csv("nombre,distrito\nA,Surco\n")
