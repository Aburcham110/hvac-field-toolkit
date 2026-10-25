"""Educational commercial rack oil call tree / checklist (stdlib).

OEM rack controls and oil systems vary — verify with rack drawings.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

DISCLAIMER = (
    "EDUCATIONAL ONLY — OEM rack oil controls, separators, and regulators vary. "
    "Verify against rack drawings and manufacturer service literature."
)

SYMPTOMS = (
    "low-oil-alarm",
    "high-separator-dp",
    "oil-logging",
    "unstable-epr",
    "general",
)


def tree(symptom: str) -> List[str]:
    base = [
        "LOTO / isolate as required before opening oil lines or separators",
        "Confirm which circuit / compressor alarmed; note oil pressure & reservoir level",
        "Check oil separator differential (inlet vs outlet) vs OEM band",
        "Inspect/replace oil filters / strainers; note bypass indicator if equipped",
        "Verify oil float / level regulator operation and equalizer lines open",
        "Confirm reservoir heater (if used) and oil viscosity/type match OEM",
        "Check oil return solenoid / orifice / check valves for stuck closed/open",
        "Look for oil traps / double risers / inverted traps on suction lines",
        "Signs of oil logging: cold sticky suction, low capacity, high SH with low amp",
        "EPR / holdback stability: hunting may push oil differently — stabilize setpoints",
        "After service: watch oil pressure through pull-down and one defrost cycle",
    ]
    extra = {
        "low-oil-alarm": [
            "Priority: mechanical oil failure vs false level probe — verify probe & wiring first",
            "Megger / amp compressor if seizure suspected; do not keep resetting oil fail",
        ],
        "high-separator-dp": [
            "Separator clogged / coalescer due — schedule changeout; check for sludge/acid",
            "Excess velocity / overcharge of oil in system after compressor changeout",
        ],
        "oil-logging": [
            "Warm suction / raise velocity; check evaporator TXV flooding vs starved",
            "Verify defrost returning liquid/oil slug paths; check header pitching",
        ],
        "unstable-epr": [
            "EPR hunting: check pilot, strainer, oversized valve, sensor location",
            "Unstable suction can intermittent oil return — fix pressure control first",
        ],
        "general": [
            "Walk the oil path: compressor → separator → reservoir → regulators → returns",
        ],
    }
    return base + extra.get(symptom, [])


def format_report(symptom: str) -> str:
    lines = [DISCLAIMER, "", f"Symptom path: {symptom}", "", "Call tree / checklist:"]
    for i, s in enumerate(tree(symptom), 1):
        lines.append(f"  [ ] {i}. {s}")
    lines += [
        "",
        "Common notes:",
        "  • After compressor change, watch for over-oiling into the rack",
        "  • Acid / moisture → oil breakdown → separator DP rise",
        "  • Parallel racks: one circuit starving oil while another floods",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational commercial rack oil checklist.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--symptom", choices=SYMPTOMS)
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
        symptom = pc("Symptom", list(SYMPTOMS), "general")
    else:
        if not ns.symptom:
            print("Need --symptom (or -i)", file=sys.stderr)
            return 2
        symptom = ns.symptom
    print(format_report(symptom))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
