"""Tests for the toolkit-hardening changes (EPA thresholds, A2L warnings, CLIs)."""

import builtins

import pytest

from hvac_field_toolkit import (
    DISCLAIMER,
    _common,
    a2l,
    airflow,
    electrical,
    leak_rate,
    psychrometrics,
    superheat,
)


def _feed(monkeypatch, answers):
    it = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda _p="": next(it))


# --- leak rate: 40 CFR 82.157(c)(2) ----------------------------------------
@pytest.mark.parametrize("cat, pct", [
    ("comfort-cooling", 10.0),
    ("commercial-refrigeration", 20.0),
    ("industrial", 30.0),
    ("other", 10.0),
])
@pytest.mark.parametrize("chem", leak_rate.CHEM_CLASSES)
def test_leak_thresholds_match_82_157(cat, pct, chem):
    r = leak_rate.analyze(full_charge_lbs=100, added_lbs=1, days=365, category=cat, chem=chem)
    assert r.threshold_pct == pct


def test_leak_transport_is_alias_for_other():
    r = leak_rate.analyze(full_charge_lbs=100, added_lbs=1, days=365, category="transport")
    assert r.category == "other"
    assert "transport" not in leak_rate.CATEGORIES


def test_leak_under_50_lb_note(capsys):
    assert leak_rate.main(["--full-charge-lbs", "20", "--added-lbs", "1", "--days", "365",
                           "--category", "transport"]) == 0
    out = capsys.readouterr().out
    assert "under 50 lb" in out and "82.157" in out


# --- A2L warnings -----------------------------------------------------------
def test_a2l_charge_limit_and_rated_equipment_warnings():
    rep = a2l.format_report("R-454B", "both")
    for needle in ("UL 60335-2-40", "ASHRAE 15", "nameplate", "MINIMUM ROOM AREA",
                   "A2L-rated recovery equipment"):
        assert needle in rep


# --- main(argv) -> int + interactive ---------------------------------------
def test_sh_sc_main_argv(capsys):
    rc = superheat.main(["-r", "R-410A", "--suction-psig", "118", "--suction-temp", "52"])
    assert rc == 0
    assert "Superheat: 12." in capsys.readouterr().out
    assert superheat.main(["-r", "R-410A"]) == 1


def test_sh_sc_interactive(monkeypatch, capsys):
    _feed(monkeypatch, ["R-410A", "118", "52", "318", "90"])
    assert superheat.main(["-i"]) == 0
    out = capsys.readouterr().out
    assert "Superheat: 12." in out and "Subcooling: 9." in out


def test_electrical_main_argv_and_interactive(monkeypatch, capsys):
    assert electrical.main(["amps", "--measured", "10", "--fla", "10"]) == 0
    assert electrical.main(["amps", "--amps", "10", "--rla", "10"]) == 0
    _feed(monkeypatch, ["imbalance", "3", "460", "455", "470"])
    assert electrical.main(["-i"]) == 0
    assert "3φ imbalance" in capsys.readouterr().out


def test_psych_main_argv_and_interactive(monkeypatch, capsys):
    assert psychrometrics.main(["--db", "75", "--rh", "50"]) == 0
    assert psychrometrics.main(["--dry-bulb", "75", "--wet-bulb", "62"]) == 0
    _feed(monkeypatch, ["75", "50", ""])
    assert psychrometrics.main(["-i"]) == 0
    assert "Approx wet-bulb" in capsys.readouterr().out


# --- option aliases ---------------------------------------------------------
@pytest.mark.parametrize("flag", ["--btuh", "--btu"])
def test_airflow_btuh_alias(flag):
    ns = airflow.build_parser().parse_args([flag, "36000"])
    assert ns.btu == 36000


# --- shared helpers ---------------------------------------------------------
def test_common_disclaimer_reexported():
    assert DISCLAIMER == _common.DISCLAIMER


def test_common_prompt_helpers(monkeypatch):
    _feed(monkeypatch, ["x", "", "bad", "b", ""])
    assert _common.prompt_float("n", 3.0) == 3.0
    assert _common.prompt_choice("c", ["a", "b"], "a") == "b"
    assert _common.prompt_text("t", "d") == "d"
