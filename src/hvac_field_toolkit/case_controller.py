"""Educational refrigerated case controller playbook (stdlib only).

High-level guidance only — verify with OEM docs/apps (e.g. Cold Chain Connect).
Does not replace Hussmann / Copeland / OEM manuals.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

DISCLAIMER = (
    "EDUCATIONAL ONLY — high-level playbook, not OEM manuals. "
    "Verify setpoints, probe maps, and defrost logic with manufacturer docs/apps "
    "(e.g. Cold Chain Connect) and the case wiring diagram."
)

FOCUSES = (
    "order-of-ops",
    "probes",
    "defrost-history",
    "eev-hunting",
    "full",
)


def section_order() -> List[str]:
    return [
        "Order of ops: PROBES first → wiring/power → then controller programming",
        "Do not reflash or replace the controller before proving sensors and harness",
        "Map probe IDs to physical locations on the case drawing",
        "Stabilize product/air temps before chasing intermittent EEV or defrost alarms",
    ]


def section_probes() -> List[str]:
    return [
        "Discharge air probe: in discharge stream, not against a metal wall falsely",
        "Return / product probe: representative of load — not in a dead corner only",
        "Defrost terminate probe: in coldest coil location per OEM (often fin pack)",
        "Compare live readings to a calibrated thermometer at the same point",
        "Open/shorted probes: check ohms vs OEM chart; reseat Molex/RJ connectors",
        "Wiring: reversed probes cause wrong cut-in/out and crazy defrost terminate",
    ]


def section_defrost() -> List[str]:
    return [
        "Read defrost history: TIME terminate vs TEMP terminate vs failsafe",
        "Always TEMP terminate early → terminate probe warm/shorted/wrong place OR too little ice",
        "Always TIME/failsafe → heaters open, contactor, drain freeze, terminate probe cold/open",
        "Too many defrosts/day → door/humidity/load; too few → iced coil / low capacity complaints",
        "After changes: watch one full refrigerate → defrost → drip → refrigerate cycle",
    ]


def section_eev() -> List[str]:
    return [
        "EEV hunting is often UPSTREAM: bad probe, wrong setpoint, unstable suction, airflow",
        "Check % open vs SH error; sensor fault codes before replacing the stepper valve",
        "Case EEV tied to rack suction: EPR/holdback swings look like valve hunting",
        "Verify superheat target and probe used for SH calculation in the controller",
    ]


def format_report(focus: str) -> str:
    blocks = []
    if focus in ("order-of-ops", "full"):
        blocks.append(("Order of operations", section_order()))
    if focus in ("probes", "full"):
        blocks.append(("Probes", section_probes()))
    if focus in ("defrost-history", "full"):
        blocks.append(("Defrost history", section_defrost()))
    if focus in ("eev-hunting", "full"):
        blocks.append(("EEV hunting as symptom", section_eev()))

    lines = [
        DISCLAIMER,
        "",
        f"Focus: {focus}",
        "",
        "High-level Hussmann / Copeland-style reminders (generic — not a manual):",
        "  • Know whether the case is self-contained vs rack-remote before changing valves",
        "  • Use OEM apps/portals for parameter lists; screenshots beat memory",
        "  • Label probes after any swap; update as-built drawings",
        "",
    ]
    n = 0
    for title, items in blocks:
        lines.append(f"## {title}")
        for item in items:
            n += 1
            lines.append(f"  [ ] {n}. {item}")
        lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational refrigerated case controller playbook.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--focus", choices=FOCUSES, default="full")
    return p


def pc(label: str, choices: List[str], default: str) -> str:
    while True:
        s = (input(f"{label} ({'/'.join(choices)}) [{default}]: ").strip() or default)
        if s in choices:
            return s
        print("Invalid choice.")


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    if ns.interactive:
        print(DISCLAIMER)
        print()
        focus = pc("Focus", list(FOCUSES), "full")
    else:
        focus = ns.focus
    print(format_report(focus))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
