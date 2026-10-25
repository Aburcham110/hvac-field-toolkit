"""Tests for migrated box-load, defrost, oil-rack, and case-controller tools."""

import subprocess
import sys

import pytest

from hvac_field_toolkit import box_load, case_controller, defrost, oil_rack


# --- box load ----------------------------------------------------------------
def test_box_load_areas():
    walls, ceil, floor, vol = box_load.areas(8, 10, 8)
    assert walls == pytest.approx(288)
    assert ceil == floor == pytest.approx(80)
    assert vol == pytest.approx(640)


def test_box_load_transmission_and_infiltration():
    # walls only effective when floor R is "none" sentinel
    assert box_load.q_tx(100, 0, 50, 25, 25, 9999.0, 60) == pytest.approx(240)
    # 60 ft3, 24 ACPD -> 1 CFM -> 1.08*dT
    assert box_load.q_inf(60, 24, 50, 0, 0) == pytest.approx(54)


def test_box_load_product_sensible():
    # 240 lb/day * cp 1.0 * 24 F / 24 h = 240 BTU/h
    assert box_load.q_prod(240, 59, 35, 1.0, 0.0, 0.0) == pytest.approx(240)


def test_box_load_suggest_band_and_safety_validation():
    assert "1 ton" in box_load.suggest(11000)
    p = box_load.build()
    a = p.parse_args(["--length", "8", "--width", "10", "--height", "8", "--safety-pct", "30"])
    with pytest.raises(ValueError):
        box_load.from_args(a)


# --- defrost -----------------------------------------------------------------
@pytest.mark.parametrize("box", defrost.BOX_TYPES)
@pytest.mark.parametrize("mode", defrost.DEFROST_MODES)
def test_defrost_report_has_steps(box, mode):
    assert defrost.steps_for(box, mode)
    assert defrost.DISCLAIMER in defrost.format_report(box, mode)


# --- oil rack ----------------------------------------------------------------
@pytest.mark.parametrize("symptom", oil_rack.SYMPTOMS)
def test_oil_rack_tree_starts_with_loto(symptom):
    steps = oil_rack.tree(symptom)
    assert steps[0].startswith("LOTO")


# --- case controller ---------------------------------------------------------
def test_case_controller_full_vs_focus():
    full = case_controller.format_report("full")
    probes = case_controller.format_report("probes")
    assert "## Order of operations" in full and "## EEV hunting as symptom" in full
    assert "## Probes" in probes and "## Defrost history" not in probes
    assert case_controller.section_order()[0].startswith("Order of ops: PROBES first")


# --- CLI ---------------------------------------------------------------------
CLI_CASES = [
    ("box_load", ["--length", "8", "--width", "10", "--height", "8"], "TOTAL w/ SF"),
    ("defrost", ["--box", "freezer", "--mode", "time-clock"], "freezer"),
    ("oil_rack", ["--symptom", "low-oil-alarm"], "LOTO"),
    ("case_controller", ["--focus", "probes"], "## Probes"),
]


@pytest.mark.parametrize("mod, args, needle", CLI_CASES)
def test_cli_basic_run_prints_disclaimer(mod, args, needle):
    out = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", *args],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "EDUCATIONAL ONLY" in out
    assert needle in out


@pytest.mark.parametrize("mod", ["box_load", "defrost", "oil_rack", "case_controller"])
def test_cli_help(mod):
    res = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", "--help"],
        capture_output=True, text=True,
    )
    assert res.returncode == 0
    assert "usage:" in res.stdout
