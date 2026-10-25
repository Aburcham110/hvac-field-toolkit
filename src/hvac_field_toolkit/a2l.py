"""Educational A2L (R-454B / R-32 / mildly flammable) field checklist (stdlib).

NOT code or legal advice. Follow OEM instructions and the Authority Having Jurisdiction (AHJ).
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from ._common import prompt_choice as pc

DISCLAIMER = (
    "EDUCATIONAL ONLY — NOT code or legal advice. "
    "Follow OEM service literature and your AHJ / local amendments for A2L work."
)

REFS = ("R-454B", "R-32", "A2L-other")
JOBS = ("service", "install", "both")

SECTIONS = [
    (
        "Pre-job",
        [
            "Identify refrigerant on nameplate (R-454B / R-32 / other A2L) and SDS",
            "Confirm space ventilation / room volume vs charge; note occupied-space limits",
            "CHARGE LIMIT / MINIMUM ROOM AREA: check total system charge (factory + field "
            "line charge) against the minimum conditioned room area on the nameplate / "
            "installation manual, per UL 60335-2-40 and ASHRAE 15 — this tool gives no "
            "numeric limits",
            "Survey ignition sources (open flame, sparking tools, smoking) — control or remove",
            "Use A2L-rated recovery machine, vacuum pump, manifold, hoses, and leak detector",
            "WARNING: recovery machine and vacuum pump must be listed/rated for A2L "
            "refrigerants (non-sparking) — do not use non-A2L-rated recovery equipment",
            "Leak detector must be rated for the A2L refrigerant in use; no open-flame "
            "(halide torch) detection",
            "Verify recovery cylinder is correct refrigerant class / residual compatible",
            "Have fire extinguisher / site emergency plan per shop policy",
        ],
    ),
    (
        "Brazing / joining",
        [
            "NEVER braze or weld on a charged system — recover to safe pressure first",
            "Purge with dry nitrogen while heating; maintain flow until cool",
            "Prefer manufacturer-approved joints (flare / press / braze) per OEM",
            "Keep hot work away from cylinders and recovered vapor vent points",
        ],
    ),
    (
        "Charge",
        [
            "Weigh-in charge only — document cylinder start/stop and total lbs",
            "No pressure-only top-off for zeotropic blends (composition shift)",
            "Charge as liquid where OEM specifies; use proper cylinder orientation",
            "Stay within nameplate / OEM additional-line charge charts",
        ],
    ),
    (
        "Commission / mitigation",
        [
            "Confirm refrigerant detection system (RDS) / sensors seated and powered if required",
            "Functional-check leak mitigation actions at high level (UL 60335-2-40 style): "
            "alarm, ventilation, compressor shutoff per OEM sequence — verify, don't invent",
            "Document sensor locations and test results in job notes",
            "Verify airflow / clearances and no blocked relief / vent paths",
        ],
    ),
    (
        "Cylinder / MOT (high-level, not legal advice)",
        [
            "Transport upright, secured; valves capped; no passenger-cabin storage",
            "Know local Maximum Occupancy / transport rules for flammable gas cylinders (AHJ)",
            "Do not mix refrigerants in recovery cylinders; label contents and date",
            "Store away from heat / ignition; check hydrostatic / requal dates on cylinders",
        ],
    ),
]


def format_report(ref: str, job: str) -> str:
    lines = [
        DISCLAIMER,
        "",
        f"Refrigerant focus: {ref}  |  Job: {job}",
        "",
    ]
    n = 0
    for title, items in SECTIONS:
        lines.append(f"## {title}")
        for item in items:
            n += 1
            lines.append(f"  [ ] {n}. {item}")
        lines.append("")
    lines += [
        "Notes:",
        "  • A2L = mildly flammable; treat ignition control and rated tools as non-optional",
        "  • UL 60335-2-40 reminders above are high-level — use OEM commission sheets",
        "  • WARNING: charge limits / minimum room area come from UL 60335-2-40, ASHRAE 15",
        "    and the equipment nameplate / installation manual — this tool provides no numbers",
        "  • WARNING: use only A2L-rated recovery equipment, vacuum pumps, and tools",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational A2L field checklist (R-454B / R-32).",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--refrigerant", choices=REFS)
    p.add_argument("--job", choices=JOBS, default="both")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    if ns.interactive:
        print(DISCLAIMER)
        print()
        ref = pc("Refrigerant", list(REFS), "R-454B")
        job = pc("Job type", list(JOBS), "both")
    else:
        if not ns.refrigerant:
            print("Need --refrigerant (or -i)", file=sys.stderr)
            return 2
        ref, job = ns.refrigerant, ns.job
    print(format_report(ref, job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
