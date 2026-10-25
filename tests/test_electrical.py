"""Tests for electrical helper calculation core."""

import pytest

from hvac_field_toolkit.electrical import (
    amp_notes,
    pct_diff,
    voltage_imbalance_1ph,
    voltage_imbalance_3ph,
)


def test_pct_diff():
    assert pct_diff(14.2, 16.0) == pytest.approx(-11.25, abs=0.01)
    assert pct_diff(18.0, 16.0) == pytest.approx(12.5, abs=0.01)
    with pytest.raises(ValueError):
        pct_diff(10, 0)


def test_amp_notes_high_and_low():
    notes = amp_notes(20.0, fla=16.0, rla=None)
    assert any("High vs FLA" in n for n in notes)

    notes = amp_notes(10.0, fla=16.0, rla=None)
    assert any("Low vs FLA" in n for n in notes)


def test_voltage_imbalance_1ph():
    pct = voltage_imbalance_1ph(240, 236)
    assert pct == pytest.approx(1.68, abs=0.1)


def test_voltage_imbalance_3ph():
    pct = voltage_imbalance_3ph(240, 238, 242)
    assert pct < 2.0
    pct_high = voltage_imbalance_3ph(240, 220, 250)
    assert pct_high > 2.0
