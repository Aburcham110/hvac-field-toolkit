"""Educational TXV / EEV diagnostic path (stdlib only).

OEM superheat targets and EEV logic vary — verify with manuals.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

DISCLAIMER = (
    "EDUCATIONAL ONLY — OEM superheat targets and EEV control logic vary. "
    "Verify with equipment manuals and controller docs."
)

VALVES = ("txv", "eev", "unknown")
SYMPTOMS = ("hunting", "high-sh", "low-sh", "general")


def checks(valve: str, symptom: str, sh: Optional[float], sc: Optional[float]) -> List[str]:
    ranked = [
        "Confirm airflow first (filter, blower, coil) before condemning the valve",
        "Measure SH at evaporator outlet / compressor per OEM; note load and OD ambient",
        "Measure SC at condenser outlet; separate charge problems from metering problems",
    ]
    if sh is not None:
        ranked.append(f"Reported SH ≈ {sh:.1f} °F — compare to OEM target for this mode/load")
    if sc is not None:
        ranked.append(f"Reported SC ≈ {sc:.1f} °F — low SC often charge; high SC can be overcharge/restriction")

    if valve in ("txv", "unknown"):
        ranked += [
            "TXV bulb: tight on suction, correct orientation, insulated, at 4–8 o'clock on large lines",
            "Equalizer tube open / not kinked (externally equalized)",
            "Inlet screen / drier restriction → high SH with starved evaporator",
            "Power element charge loss → valve closed / high SH",
        ]
    if valve in ("eev", "unknown"):
        ranked += [
            "EEV: do NOT replace the valve first — prove sensors and % open command",
            "Compare controller % open to actual SH error (hunting vs stuck)",
            "Sensor faults (supply/suction/pressure) drive wrong EEV position",
            "Stepper wiring / polarity / lost steps after power interrupt",
        ]

    if symptom == "hunting":
        ranked.insert(3, "Hunting: unstable load, oversized valve, bulb loose, or EEV PID/sensors")
    elif symptom == "high-sh":
        ranked.insert(3, "High SH: underfeed — restriction, loss of charge, valve closed, low airflow less common")
    elif symptom == "low-sh":
        ranked.insert(3, "Low SH: overfeed / flood risk — bulb warm, valve stuck open, EEV commanded open")

    ranked += [
        "Charge: weigh-in / OEM charts; blends are not pressure-only topped off",
        "Document SH/SC, valve type, bulb location, and EEV % before changing parts",
    ]
    return ranked


def format_report(valve: str, symptom: str, sh: Optional[float], sc: Optional[float]) -> str:
    lines = [
        DISCLAIMER,
        "",
        f"Valve path: {valve}  |  Symptom: {symptom}",
        "",
        "Ranked checks:",
    ]
    for i, c in enumerate(checks(valve, symptom, sh, sc), 1):
        lines.append(f"  {i}. {c}")
    lines += [
        "",
        "Parts to consider (last, after sensors/airflow/charge):",
        "  • Filter-drier / inlet screen",
        "  • TXV power element or valve body",
        "  • EEV stepper / valve only after command vs position proven",
        "  • Pressure/temp sensors feeding EEV",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational TXV / EEV diagnostic path.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--valve", choices=VALVES, default="unknown")
    p.add_argument("--symptom", choices=SYMPTOMS, default="general")
    p.add_argument("--sh", type=float, default=None)
    p.add_argument("--sc", type=float, default=None)
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
        valve = pc("Valve", list(VALVES), "txv")
        symptom = pc("Symptom", list(SYMPTOMS), "hunting")
        raw = input("SH °F (blank skip): ").strip()
        sh = float(raw) if raw else None
        raw = input("SC °F (blank skip): ").strip()
        sc = float(raw) if raw else None
    else:
        valve, symptom, sh, sc = ns.valve, ns.symptom, ns.sh, ns.sc
    print(format_report(valve, symptom, sh, sc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
