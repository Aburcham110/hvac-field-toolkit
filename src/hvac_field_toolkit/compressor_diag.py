"""Educational compressor symptom diagnostic tree (stdlib).

Includes LOTO / safety reminders. Incomplete — verify with OEM.
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional, Tuple

DISCLAIMER = (
    "EDUCATIONAL ONLY — incomplete diagnostic stubs. "
    "Follow LOTO, PPE, and OEM procedures. Live voltage and refrigerant hazards."
)

SYMPTOMS = (
    "high-discharge-temp",
    "floodback",
    "short-cycle",
    "locked-rotor",
    "high-amps",
)


def tree(symptom: str, sh: Optional[float], sc: Optional[float]) -> Tuple[List[str], List[str]]:
    """Return (ranked checks, parts)."""
    safety = [
        "LOTO electrical before meggering or changing compressor",
        "Recover refrigerant safely before opening the circuit",
        "Verify capacitor discharge / inverter DC bus wait time if applicable",
    ]
    ctx = []
    if sh is not None:
        ctx.append(f"Reported SH ≈ {sh:.1f} °F")
    if sc is not None:
        ctx.append(f"Reported SC ≈ {sc:.1f} °F")

    tables: Dict[str, Tuple[List[str], List[str]]] = {
        "high-discharge-temp": (
            [
                "Confirm true discharge line temp 6–8\" from compressor (not muffler)",
                "High SH / low charge / restriction → hot gas; check SH/SC and drier ΔT",
                "Non-condensables / dirty condenser / failed OD fan → high head + DLT",
                "Wrong oil / low oil / failed cooling (refrigerant-cooled scroll)",
                "Overheated windings: check amp, voltage imbalance, shorted turns",
            ],
            ["Condenser fan motor", "Filter-drier", "TXV/piston", "Compressor (last)"],
        ),
        "floodback": (
            [
                "Low SH at compressor: TXV hunting, oversized orifice, fan-off defrost return",
                "Evaporator overfeed / low load / iced coil",
                "Crankcase heater offline; migration on off-cycle",
                "Check accumulator (if equipped) and piping pitch",
            ],
            ["TXV", "Crankcase heater", "Accumulator", "Coil / airflow parts"],
        ),
        "short-cycle": (
            [
                "Control: thermostat anticipator/cycle rate, short-cycle timer, pressure switches",
                "High head cutout: dirty condenser, overcharge, non-condensables",
                "Low pressure cutout: low charge, restriction, low airflow",
                "Electrical: failing contactor chatter, loose lugs, low voltage",
            ],
            ["Contactor", "HP/LP switches", "Capacitor", "Thermostat"],
        ),
        "locked-rotor": (
            [
                "Do not repeatedly reset — risk of winding damage",
                "Hard-start / capacitor open? Measure µF and voltage under load",
                "Seized bearings / flooded start / equalized pressures not equalizing",
                "Single-phasing on 3-phase; check fuses/contacts",
                "Megger windings after LOTO; compare to OEM",
            ],
            ["Start/run capacitor", "Hard-start kit", "Contactor", "Compressor"],
        ),
        "high-amps": (
            [
                "Compare RLA/FLA on nameplate to measured clamp amps",
                "High head pressure (airflow/charge) raises amps — fix air-side first",
                "Low voltage / imbalance; tight bearings; liquid flood increasing density",
                "SH/SC context: low SH + high amps → possible flood; high SH + high amps → head/airflow",
            ],
            ["Capacitor", "Contactor", "Condenser fan", "Compressor"],
        ),
    }
    checks, parts = tables[symptom]
    if sh is not None and symptom in ("high-discharge-temp", "high-amps", "floodback"):
        if sh < 5:
            checks = ["Context: low SH — prioritize floodback / overfeed checks"] + checks
        elif sh > 30:
            checks = ["Context: high SH — prioritize low charge / restriction / low load"] + checks
    ranked = safety + (["; ".join(ctx)] if ctx else []) + checks
    return ranked, parts


def format_report(symptom: str, sh: Optional[float], sc: Optional[float]) -> str:
    checks, parts = tree(symptom, sh, sc)
    lines = [DISCLAIMER, "", f"Symptom: {symptom}", "", "Ranked checks:"]
    for i, c in enumerate(checks, 1):
        lines.append(f"  {i}. {c}")
    lines += ["", "Parts to consider (not a replace-all list):"]
    for p in parts:
        lines.append(f"  • {p}")
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational compressor diagnostic tree.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--symptom", choices=SYMPTOMS)
    p.add_argument("--sh", type=float, default=None, help="Superheat °F context")
    p.add_argument("--sc", type=float, default=None, help="Subcooling °F context")
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
        symptom = pc("Symptom", list(SYMPTOMS), "high-amps")
        raw = input("SH °F (blank skip): ").strip()
        sh = float(raw) if raw else None
        raw = input("SC °F (blank skip): ").strip()
        sc = float(raw) if raw else None
    else:
        if not ns.symptom:
            print("Need --symptom (or -i)", file=sys.stderr)
            return 2
        symptom, sh, sc = ns.symptom, ns.sh, ns.sc
    print(format_report(symptom, sh, sc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
