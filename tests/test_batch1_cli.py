"""Tests for migrated airflow, duct/static, and charge tools."""

import subprocess
import sys

import pytest

from hvac_field_toolkit import airflow, charge, duct_static


# --- airflow -----------------------------------------------------------------
def test_airflow_cooling_dt_and_band():
    r = airflow.analyze(system="res-ac", supply_f=55, return_f=75)
    assert r.measured_dt == pytest.approx(20)
    assert r.status == "in-band"


def test_airflow_heating_high_and_cfm():
    r = airflow.analyze(system="furnace", supply_f=150, return_f=70, btuh=80000)
    assert r.measured_dt == pytest.approx(80)
    assert r.status == "high"
    assert r.cfm == pytest.approx(80000 / (1.08 * 80))


def test_airflow_kw_to_btuh_and_bad_system():
    r = airflow.analyze(system="hp-heat", supply_f=95, return_f=70, kw=10)
    assert r.heat_btuh == pytest.approx(34120)
    with pytest.raises(ValueError):
        airflow.analyze(system="boiler", supply_f=1, return_f=2)


# --- duct / static -----------------------------------------------------------
def test_duct_area_rect_and_round():
    assert duct_static.area_sqft("rect", 12, 12, None) == pytest.approx(1.0)
    assert duct_static.area_sqft("round", 0, None, 12) == pytest.approx(0.7854, abs=1e-3)
    with pytest.raises(ValueError):
        duct_static.area_sqft("round", 0, None, None)


def test_duct_velocity_and_esp_sum():
    r = duct_static.analyze(
        cfm=1200, shape="rect", width_in=20, height_in=10, diameter_in=None,
        duct_type="supply-main", filter_dp_in=0.25, coil_dp_in=0.4, other_dp_in=0.0,
    )
    text = "\n".join(r.lines)
    assert "864 FPM" in text  # 1200 / (20*10/144)
    assert "0.65 in. w.c." in text


# --- charge ------------------------------------------------------------------
def test_charge_split_ac_billable_and_add():
    e = charge.estimate(
        refrigerant="R-410A", system="split-ac", factory_lbs=7.5,
        liquid_ft=40, liquid_od="3/8", suction_ft=0, current_lbs=7.5,
    )
    inc = charge.INCLUDED_LIQUID_FT["split-ac"]
    billable = max(0.0, 40 - inc)
    assert e.billable_liquid_ft == pytest.approx(billable)
    expected_add = billable * charge.LIQUID_OZ_PER_FT["R-410A"]["3/8"] / 16
    assert e.add_lbs == pytest.approx(expected_add)
    assert e.delta_lbs == pytest.approx(expected_add)


def test_charge_recover_and_aliases():
    e = charge.estimate(
        refrigerant="410a", system="package", factory_lbs=10, liquid_ft=0,
        liquid_od="0.375", current_lbs=12,
    )
    assert e.refrigerant == "R-410A"
    assert e.delta_lbs == pytest.approx(-2.0)
    with pytest.raises(ValueError):
        charge.norm_ref("R-999")


# --- CLI ---------------------------------------------------------------------
CLI_CASES = [
    ("airflow", ["--system", "res-ac", "--supply", "55", "--return-temp", "75"], "Measured ΔT"),
    ("duct_static", ["--cfm", "1200", "--width-in", "20", "--height-in", "10"], "velocity"),
    ("charge", ["--system", "split-ac", "--refrigerant", "R-410A", "--factory-lbs", "7.5",
                "--liquid-ft", "40", "--liquid-od", "3/8"], "Estimated total charge"),
]


@pytest.mark.parametrize("mod, args, needle", CLI_CASES)
def test_cli_basic_run_prints_disclaimer(mod, args, needle):
    out = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", *args],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "EDUCATIONAL ONLY" in out
    assert needle in out


@pytest.mark.parametrize("mod", ["airflow", "duct_static", "charge"])
def test_cli_help(mod):
    res = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", "--help"],
        capture_output=True, text=True,
    )
    assert res.returncode == 0
    assert "EDUCATIONAL ONLY" in res.stdout
