"""Tests for migrated A2L checklist, nameplate fault codes, and job-log tools."""

import json
import subprocess
import sys

import pytest

from hvac_field_toolkit import a2l, job_log, nameplate_faults as nf


# --- A2L ---------------------------------------------------------------------
@pytest.mark.parametrize("ref", a2l.REFS)
def test_a2l_report_numbered_and_disclaimed(ref):
    rep = a2l.format_report(ref, "both")
    total = sum(len(items) for _, items in a2l.SECTIONS)
    assert f"[ ] {total}." in rep
    assert rep.count(a2l.DISCLAIMER) == 2
    assert f"Refrigerant focus: {ref}" in rep


def test_a2l_requires_refrigerant():
    assert a2l.main([]) == 2


# --- nameplate / fault codes -------------------------------------------------
def test_lookup_brand_then_generic_case_insensitive():
    hits = nf.lookup_fault("Car rier", "33")
    assert [s for s, _ in hits] == ["carrier"]
    assert [s for s, _ in nf.lookup_fault("Trane", "e1")] == ["generic"]
    assert nf.lookup_fault("trane", "e.172")[0][0] == "trane"
    assert nf.lookup_fault("generic", "ZZZ") == []


def test_save_card_appends_json(tmp_path):
    store = tmp_path / "cards.json"
    nf.save_card(store, nf.Nameplate(brand="Carrier", fault_code="33"))
    nf.save_card(store, nf.Nameplate(brand="Trane"))
    data = nf.load_store(store)
    assert len(data) == 2 and data[0]["brand"] == "Carrier"


# --- job log -----------------------------------------------------------------
def _args(*extra):
    return job_log.build_parser().parse_args(list(extra))


def test_job_log_defaults():
    job = job_log.from_args(_args("--date", "2026-10-25", "--leak-found", "y"))
    assert job.lbs_added == "0" and job.lbs_recovered == "0"
    assert job.leak_found == "Y" and job.leak_repaired == "N"
    assert job.customer_copy_given == "Y" and job.tech_file_copy == "Y"


def test_job_log_renders_both_formats():
    job = job_log.from_args(_args("--date", "2026-10-25", "--customer", "Acme"))
    assert "Customer:          Acme" in job.render_text()
    md = job.render_markdown()
    assert md.startswith("# HVAC/R Service Job Log") and job_log.DISCLAIMER in md


def test_job_log_json_in_and_output(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps({"customer": "Acme", "serial": "S123"}))
    out = tmp_path / "out.md"
    assert job_log.main(["--json-in", str(src), "--format", "markdown", "-o", str(out)]) == 0
    body = out.read_text()
    assert "| Serial | S123 |" in body and "Acme" in body


# --- CLI ---------------------------------------------------------------------
def _run(mod, *args, **kw):
    return subprocess.run(
        [sys.executable, "-m", f"hvac_field_toolkit.{mod}", *args],
        capture_output=True, text=True, **kw,
    )


CLI_CASES = [
    ("a2l", ["--refrigerant", "R-32", "--job", "service"], "EDUCATIONAL ONLY", "## Pre-job"),
    ("nameplate_faults", ["--brand", "Carrier", "--code", "33", "--store", "/nonexistent/x.json"],
     "EDUCATIONAL ONLY", "Carrier-style"),
    ("nameplate_faults", ["--list-codes"], "EDUCATIONAL ONLY", "[generic]"),
    ("job_log", ["--date", "2026-10-25", "--technician", "A. Tech"],
     "NOT an EPA", "Technician:        A. Tech"),
]


@pytest.mark.parametrize("mod, args, disclaimer, needle", CLI_CASES)
def test_cli_basic_run(mod, args, disclaimer, needle):
    out = _run(mod, *args, check=True).stdout
    assert disclaimer in out and needle in out


@pytest.mark.parametrize("mod", ["a2l", "nameplate_faults", "job_log"])
def test_cli_help(mod):
    res = _run(mod, "--help")
    assert res.returncode == 0 and "usage:" in res.stdout
