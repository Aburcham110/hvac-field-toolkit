"""Tests for migrated compressor, TXV/EEV, vacuum, and leak-rate tools."""

import subprocess
import sys

import pytest

from hvac_field_toolkit import compressor_diag, leak_rate, txv_eev, vacuum


# --- compressor --------------------------------------------------------------
@pytest.mark.parametrize("symptom", compressor_diag.SYMPTOMS)
def test_compressor_tree_starts_with_loto(symptom):
    checks, parts = compressor_diag.tree(symptom, None, None)
    assert checks[0].startswith("LOTO")
    assert parts


def test_compressor_sh_context_prioritized():
    low, _ = compressor_diag.tree("high-amps", 3, None)
    high, _ = compressor_diag.tree("high-amps", 35, None)
    assert any("low SH" in c for c in low)
    assert any("high SH" in c for c in high)


# --- TXV / EEV ---------------------------------------------------------------
def test_txv_eev_airflow_first_and_valve_specific():
    eev = txv_eev.checks("eev", "hunting", 3, 10)
    assert eev[0].startswith("Confirm airflow first")
    assert any("do NOT replace the valve first" in c for c in eev)
    assert not any("TXV bulb" in c for c in eev)
    txv = txv_eev.checks("txv", "high-sh", 25, None)
    assert any("TXV bulb" in c for c in txv)
    assert any("High SH" in c for c in txv)


# --- vacuum ------------------------------------------------------------------
def test_vacuum_decay_bands():
    ok = vacuum.interpret_decay(400, 450, 10)
    assert "+50" in ok[0] and "acceptable hold" in ok[3]
    fast = vacuum.interpret_decay(400, 5000, 10)
    assert "Fast rise" in fast[3]
    with pytest.raises(ValueError):
        vacuum.interpret_decay(400, 450, 0)


def test_vacuum_coach_mentions_500_microns():
    assert any("500 microns" in s for s in vacuum.coach_lines())


# --- leak rate ---------------------------------------------------------------
def test_leak_rate_annualized_math():
    # 10 lb added to 100 lb system over half a year -> 20 %/yr
    assert leak_rate.annualized_leak_pct(100, 10, 182.5) == pytest.approx(20.0)
    with pytest.raises(ValueError):
        leak_rate.annualized_leak_pct(0, 1, 30)


def test_leak_rate_threshold_by_chem():
    hfc = leak_rate.analyze(full_charge_lbs=100, added_lbs=12.5, days=182.5,
                            category="commercial-refrigeration", chem="hfc")
    hcfc = leak_rate.analyze(full_charge_lbs=100, added_lbs=12.5, days=182.5,
                             category="commercial-refrigeration", chem="hcfc")
    assert hfc.annualized_pct == pytest.approx(25.0)
    assert hfc.over is True
    assert hcfc.over is False


# --- CLI ---------------------------------------------------------------------
CLI_CASES = [
    ("compressor_diag", ["--symptom", "high-amps", "--sh", "4"], "Ranked checks", "EDUCATIONAL ONLY"),
    ("txv_eev", ["--valve", "eev", "--symptom", "hunting"], "Confirm airflow first", "EDUCATIONAL ONLY"),
    ("vacuum", ["--mode", "interpret-decay", "--start-micron", "400",
                "--after-micron", "450", "--minutes", "10"], "Hold test", "EDUCATIONAL ONLY"),
    ("leak_rate", ["--full-charge-lbs", "100", "--added-lbs", "10", "--days", "182.5",
                   "--category", "commercial-refrigeration"], "Annualized leak rate",
     "NOT A COMPLIANCE SYSTEM"),
]


@pytest.mark.parametrize("mod, args, needle, banner", CLI_CASES)
def test_cli_basic_run_prints_disclaimer(mod, args, needle, banner):
    out = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", *args],
        capture_output=True, text=True, check=True,
    ).stdout
    assert banner in out
    assert needle in out


@pytest.mark.parametrize("mod", ["compressor_diag", "txv_eev", "vacuum", "leak_rate"])
def test_cli_help(mod):
    res = subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", "--help"],
        capture_output=True, text=True,
    )
    assert res.returncode == 0
    assert "usage:" in res.stdout
