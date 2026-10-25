"""Tests for superheat / subcooling calculation core and PT tables.

Reference psig values: CoolProp 8.0.0 (HEOS), psig = psia - 14.696, generated
independently of the table by tools/gen_pt_tables.py. R-454B is additionally
checked against the Chemours Opteon XL41 Temperature-Pressure Data (C-10270 rev 07-23).
"""

import pytest

from hvac_field_toolkit.superheat import (
    PT_TABLES,
    REFRIGERANTS,
    sat_pressure,
    sat_temp,
    sc_guide,
    sh_guide,
    subcooling,
    superheat,
)

# refrigerant -> {temp_F: (dew_psig, bubble_psig)}
COOLPROP_REF = {
    "R-410A": {40: (118.4, 118.8), 100: (317.6, 318.5)},
    "R-22": {40: (68.6, 68.6), 100: (195.9, 195.9)},
    "R-134a": {40: (35.0, 35.0), 100: (124.2, 124.2)},
    "R-404A": {40: (85.4, 86.9), 100: (234.7, 236.8)},
    "R-407C": {40: (63.2, 80.2), 100: (196.1, 225.5)},
    "R-32": {40: (121.0, 121.0), 100: (325.7, 325.7)},
    "R-454B": {40: (107.5, 113.2), 100: (291.9, 303.3)},
}
CHEMOURS_XL41 = {40: (107.0, 112.0), 100: (291.0, 300.7)}

CASES = [
    (ref, t, side, pts[0] if side == "dew" else pts[1])
    for ref, by_t in COOLPROP_REF.items()
    for t, pts in by_t.items()
    for side in ("dew", "bubble")
]


def test_all_refrigerants_covered():
    assert set(COOLPROP_REF) == set(REFRIGERANTS) == set(PT_TABLES)


@pytest.mark.parametrize("ref, temp, side, psig", CASES)
def test_sat_temp_matches_coolprop(ref, temp, side, psig):
    assert sat_temp(ref, psig, side) == pytest.approx(temp, abs=1.0)


@pytest.mark.parametrize("temp", [40, 100])
def test_r454b_matches_chemours_chart(temp):
    dew, bubble = CHEMOURS_XL41[temp]
    assert sat_temp("R-454B", dew, "dew") == pytest.approx(temp, abs=1.0)
    assert sat_temp("R-454B", bubble, "bubble") == pytest.approx(temp, abs=1.0)


def test_tables_monotonic_and_bubble_not_below_dew():
    for ref, rows in PT_TABLES.items():
        for a, b in zip(rows, rows[1:]):
            assert b[0] > a[0] and b[1] > a[1] and b[2] > a[2], ref
        for _, dew, bub in rows:
            assert bub >= dew, ref


def test_sat_pressure_roundtrip():
    assert sat_pressure("R-410A", 40) == pytest.approx(118.4, abs=0.1)
    assert sat_pressure("R-407C", 100, "bubble") == pytest.approx(225.5, abs=0.1)
    assert sat_temp("R-22", sat_pressure("R-22", 47)) == pytest.approx(47, abs=0.05)


def test_sat_temp_errors():
    with pytest.raises(ValueError, match="outside table"):
        sat_temp("R-410A", 900)
    with pytest.raises(ValueError, match="Unsupported"):
        sat_temp("R-999", 100)
    with pytest.raises(ValueError, match="side"):
        sat_temp("R-410A", 100, "mid")


def test_superheat_and_subcooling_r410a():
    # 118.4 psig suction ~ 40 °F dew; 52 °F suction line -> ~12 °F SH
    assert superheat("R-410A", 118.4, 52) == pytest.approx(12.0, abs=0.5)
    # 318.5 psig liquid ~ 100 °F bubble; 90 °F liquid line -> ~10 °F SC
    assert subcooling("R-410A", 318.5, 90) == pytest.approx(10.0, abs=0.5)


def test_blend_uses_dew_for_sh_and_bubble_for_sc():
    # R-407C: same 40 °F saturation, very different pressures on each curve
    assert superheat("R-407C", 63.2, 50) == pytest.approx(10.0, abs=0.5)
    assert subcooling("R-407C", 80.2, 30) == pytest.approx(10.0, abs=0.5)
    # R-454B with Chemours chart pressures (table is CoolProp; agree within 1 °F)
    assert superheat("R-454B", 107.0, 50) == pytest.approx(10.0, abs=1.0)
    assert subcooling("R-454B", 300.7, 90) == pytest.approx(10.0, abs=1.0)


def test_guides():
    assert "floodback" in sh_guide(3).lower()
    assert "target" in sh_guide(12).lower()
    assert "undercharge" in sc_guide(3).lower() or "low" in sc_guide(3).lower()
    assert "target" in sc_guide(10).lower()
