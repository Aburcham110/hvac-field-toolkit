"""Tests for superheat / subcooling calculation core."""

import pytest

from hvac_field_toolkit.superheat import (
    sat_temp,
    superheat,
    subcooling,
    sh_guide,
    sc_guide,
)


def test_sat_temp_known_points_r410a():
    assert sat_temp("R-410A", 100) == pytest.approx(14.0, abs=0.1)
    assert sat_temp("R-410A", 118) == pytest.approx(23.0, abs=0.1)
    assert sat_temp("R-410A", 200) == pytest.approx(55.0, abs=0.1)


def test_sat_temp_interpolation():
    t = sat_temp("R-410A", 105)
    assert 14 < t < 19


def test_sat_temp_out_of_range():
    with pytest.raises(ValueError, match="outside table"):
        sat_temp("R-410A", 30)
    with pytest.raises(ValueError, match="Unsupported"):
        sat_temp("R-999", 100)


def test_superheat_and_subcooling():
    sh = superheat("R-410A", 118, 40)
    assert sh == pytest.approx(17.0, abs=0.5)

    sc = subcooling("R-410A", 200, 50)
    assert sc == pytest.approx(5.0, abs=0.5)


def test_guides():
    assert "floodback" in sh_guide(3).lower()
    assert "target" in sh_guide(12).lower()
    assert "undercharge" in sc_guide(3).lower() or "low" in sc_guide(3).lower()
    assert "target" in sc_guide(10).lower()
