"""Educational HVAC/R service job-log notes CLI (stdlib).

Structured call notes + EPA 608–style fields for technician file / customer copy.
NOT legal advice and NOT a compliance system.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

DISCLAIMER = (
    "EDUCATIONAL / RECORD-KEEPING AID ONLY — NOT legal advice, NOT an EPA "
    "compliance system, and NOT a substitute for certified technician judgment "
    "or official forms required by law or your employer."
)


@dataclass
class JobLog:
    date: str = ""
    technician: str = ""
    customer: str = ""
    site_address: str = ""
    equipment: str = ""
    model: str = ""
    serial: str = ""
    refrigerant_type: str = ""
    lbs_added: str = ""
    lbs_recovered: str = ""
    leak_found: str = ""  # Y/N
    leak_repaired: str = ""  # Y/N
    leak_notes: str = ""
    work_performed: str = ""
    parts_used: str = ""
    follow_ups: str = ""
    # EPA 608–style technician-file / customer-copy fields (educational labels)
    cert_type_noted: str = ""  # e.g. Type I/II/III/Universal — self-attested note only
    system_charge_lbs: str = ""
    recovery_equipment_id: str = ""
    vacuum_level_microns: str = ""
    customer_copy_given: str = ""  # Y/N
    tech_file_copy: str = ""  # Y/N
    extra_notes: str = ""

    def render_text(self) -> str:
        lines = [
            "=" * 64,
            "HVAC/R SERVICE JOB LOG (educational)",
            DISCLAIMER,
            "=" * 64,
            "",
            f"Date:              {self.date}",
            f"Technician:        {self.technician}",
            f"Customer:          {self.customer}",
            f"Site:              {self.site_address}",
            "",
            "--- Equipment ---",
            f"Equipment:         {self.equipment}",
            f"Model:             {self.model}",
            f"Serial:            {self.serial}",
            "",
            "--- Refrigerant / leak (608-style fields; NOT compliance) ---",
            f"Refrigerant type:  {self.refrigerant_type}",
            f"System charge lbs: {self.system_charge_lbs}",
            f"Lbs added:         {self.lbs_added}",
            f"Lbs recovered:     {self.lbs_recovered}",
            f"Recovery equip ID: {self.recovery_equipment_id}",
            f"Vacuum (microns):  {self.vacuum_level_microns}",
            f"Leak found (Y/N):  {self.leak_found}",
            f"Leak repaired:     {self.leak_repaired}",
            f"Leak notes:        {self.leak_notes}",
            f"Cert type noted:   {self.cert_type_noted}",
            f"Customer copy:     {self.customer_copy_given}",
            f"Tech file copy:    {self.tech_file_copy}",
            "",
            "--- Work ---",
            f"Work performed:    {self.work_performed}",
            f"Parts used:        {self.parts_used}",
            f"Follow-ups:        {self.follow_ups}",
            f"Extra notes:       {self.extra_notes}",
            "",
            DISCLAIMER,
            "=" * 64,
        ]
        return "\n".join(lines) + "\n"

    def render_markdown(self) -> str:
        return (
            f"# HVAC/R Service Job Log (educational)\n\n"
            f"> {DISCLAIMER}\n\n"
            f"**Date:** {self.date}  \n"
            f"**Technician:** {self.technician}  \n"
            f"**Customer:** {self.customer}  \n"
            f"**Site:** {self.site_address}\n\n"
            f"## Equipment\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Equipment | {self.equipment} |\n"
            f"| Model | {self.model} |\n"
            f"| Serial | {self.serial} |\n\n"
            f"## Refrigerant / leak (608-style; NOT compliance)\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Refrigerant type | {self.refrigerant_type} |\n"
            f"| System charge (lbs) | {self.system_charge_lbs} |\n"
            f"| Lbs added | {self.lbs_added} |\n"
            f"| Lbs recovered | {self.lbs_recovered} |\n"
            f"| Recovery equipment ID | {self.recovery_equipment_id} |\n"
            f"| Vacuum (microns) | {self.vacuum_level_microns} |\n"
            f"| Leak found | {self.leak_found} |\n"
            f"| Leak repaired | {self.leak_repaired} |\n"
            f"| Leak notes | {self.leak_notes} |\n"
            f"| Cert type noted | {self.cert_type_noted} |\n"
            f"| Customer copy given | {self.customer_copy_given} |\n"
            f"| Tech file copy | {self.tech_file_copy} |\n\n"
            f"## Work\n\n"
            f"**Work performed:** {self.work_performed}\n\n"
            f"**Parts used:** {self.parts_used}\n\n"
            f"**Follow-ups:** {self.follow_ups}\n\n"
            f"**Extra notes:** {self.extra_notes}\n\n"
            f"---\n\n*{DISCLAIMER}*\n"
        )


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{label}{suffix}: ").strip()
    return val if val else default


def yn(label: str, default: str = "N") -> str:
    while True:
        v = prompt(label + " (Y/N)", default).upper()
        if v in ("Y", "N", "YES", "NO"):
            return "Y" if v.startswith("Y") else "N"
        print("Enter Y or N.")


def interactive() -> JobLog:
    print("HVAC/R job-log notes (educational)\n" + DISCLAIMER + "\n")
    today = datetime.now().strftime("%Y-%m-%d")
    j = JobLog(
        date=prompt("Date (YYYY-MM-DD)", today),
        technician=prompt("Technician name"),
        customer=prompt("Customer / company"),
        site_address=prompt("Site address"),
        equipment=prompt("Equipment (e.g. 3-ton RTU)"),
        model=prompt("Model"),
        serial=prompt("Serial"),
        refrigerant_type=prompt("Refrigerant type", "R-410A"),
        system_charge_lbs=prompt("System charge (lbs, if known)"),
        lbs_added=prompt("Lbs added", "0"),
        lbs_recovered=prompt("Lbs recovered", "0"),
        recovery_equipment_id=prompt("Recovery equipment ID"),
        vacuum_level_microns=prompt("Final vacuum (microns)"),
        leak_found=yn("Leak found"),
        leak_repaired=yn("Leak repaired"),
        leak_notes=prompt("Leak notes"),
        cert_type_noted=prompt("Cert type noted (I/II/III/Universal — self note only)"),
        customer_copy_given=yn("Customer copy given", "Y"),
        tech_file_copy=yn("Tech file copy retained", "Y"),
        work_performed=prompt("Work performed"),
        parts_used=prompt("Parts used"),
        follow_ups=prompt("Follow-ups"),
        extra_notes=prompt("Extra notes"),
    )
    return j


def from_args(a: argparse.Namespace) -> JobLog:
    return JobLog(
        date=a.date or datetime.now().strftime("%Y-%m-%d"),
        technician=a.technician or "",
        customer=a.customer or "",
        site_address=a.site or "",
        equipment=a.equipment or "",
        model=a.model or "",
        serial=a.serial or "",
        refrigerant_type=a.refrigerant or "",
        system_charge_lbs=a.system_charge_lbs or "",
        lbs_added=a.lbs_added or "0",
        lbs_recovered=a.lbs_recovered or "0",
        recovery_equipment_id=a.recovery_equip or "",
        vacuum_level_microns=a.vacuum_microns or "",
        leak_found=(a.leak_found or "N").upper()[:1],
        leak_repaired=(a.leak_repaired or "N").upper()[:1],
        leak_notes=a.leak_notes or "",
        cert_type_noted=a.cert_type or "",
        customer_copy_given=(a.customer_copy or "Y").upper()[:1],
        tech_file_copy=(a.tech_file or "Y").upper()[:1],
        work_performed=a.work or "",
        parts_used=a.parts or "",
        follow_ups=a.follow_ups or "",
        extra_notes=a.extra or "",
    )


def export(job: JobLog, fmt: str, out: Optional[str]) -> None:
    body = job.render_markdown() if fmt == "markdown" else job.render_text()
    if out:
        Path(out).write_text(body, encoding="utf-8")
        print(f"Wrote {fmt} job summary to {out}", file=sys.stderr)
        print(DISCLAIMER, file=sys.stderr)
    else:
        sys.stdout.write(body)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Educational HVAC/R job-log notes with 608-style fields. "
            "NOT legal advice / NOT a compliance system."
        )
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--format", choices=["text", "markdown"], default="text")
    p.add_argument("-o", "--output", help="Write summary to file (else stdout)")
    p.add_argument("--date")
    p.add_argument("--technician")
    p.add_argument("--customer")
    p.add_argument("--site")
    p.add_argument("--equipment")
    p.add_argument("--model")
    p.add_argument("--serial")
    p.add_argument("--refrigerant")
    p.add_argument("--system-charge-lbs")
    p.add_argument("--lbs-added")
    p.add_argument("--lbs-recovered")
    p.add_argument("--recovery-equip")
    p.add_argument("--vacuum-microns")
    p.add_argument("--leak-found", choices=["Y", "N", "y", "n"])
    p.add_argument("--leak-repaired", choices=["Y", "N", "y", "n"])
    p.add_argument("--leak-notes")
    p.add_argument("--cert-type")
    p.add_argument("--customer-copy", choices=["Y", "N", "y", "n"])
    p.add_argument("--tech-file", choices=["Y", "N", "y", "n"])
    p.add_argument("--work")
    p.add_argument("--parts")
    p.add_argument("--follow-ups")
    p.add_argument("--extra")
    p.add_argument(
        "--json-in",
        help="Load fields from a JSON file (keys match JobLog fields)",
    )
    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.json_in:
            data = json.loads(Path(args.json_in).read_text(encoding="utf-8"))
            job = JobLog(**{k: data.get(k, "") for k in JobLog.__dataclass_fields__})
        elif args.interactive or len(sys.argv) == 1:
            job = interactive()
        else:
            job = from_args(args)
        export(job, args.format, args.output)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(main(["-i"]))
    sys.exit(main())
