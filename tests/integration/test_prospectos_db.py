import pytest

from visible_ia.prospectos import list_unseen, mark_seen

pytestmark = pytest.mark.integration


def test_list_unseen_skips_do_not_contact_and_marks_seen(tx):
    with tx.cursor() as cur:
        cur.execute("update public.prospects set seen = true where not seen")  # rolled back
        cur.executemany(
            "insert into public.prospects (name, clinic_name, category_code, district, contact, "
            "utm, consent, do_not_contact, consent_version) "
            "values (%s, %s, 'IMP', 'Miraflores', %s, %s, true, %s, '2026-09-28')",
            [
                ("Ana", "Clínica Uno", "+51 911 111 111", '{"utm_source": "wa"}', False),
                ("Luis", "Clínica Dos", "luis@x.pe", None, False),
                ("Eva", "Clínica Tres", "+51 922 222 222", None, True),  # asked not to be contacted
            ],
        )
    rows = list_unseen(tx)
    assert [p.clinic_name for p in rows] == ["Clínica Uno", "Clínica Dos"]
    assert rows[0].source == "wa"
    mark_seen(tx, [p.id for p in rows])
    assert list_unseen(tx) == []
