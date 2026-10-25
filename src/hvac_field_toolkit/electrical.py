"""Electrical field checks (FLA/RLA, capacitors, voltage imbalance)."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from ._common import DISCLAIMER, prompt_choice, prompt_float, prompt_optional_float

LOTO = (
    "SAFETY / LOTO: De-energize, lock/tag disconnect, verify zero energy with "
    "a meter, and treat capacitors as charged until discharged per OEM procedure."
)


def pct_diff(measured: float, rated: float) -> float:
    """Percentage difference of measured vs rated."""
    if rated == 0:
        raise ValueError("Rated value cannot be 0.")
    return (measured - rated) / abs(rated) * 100.0


def amp_notes(measured: float, fla: Optional[float], rla: Optional[float]) -> list[str]:
    """Return educational notes comparing measured amps to FLA/RLA."""
    notes = []
    if fla is not None:
        d = pct_diff(measured, fla)
        if measured > fla * 1.10:
            note = (
                "High vs FLA — check load, airflow, charge, voltage, and shorted windings "
                "(approx)."
            )
        elif measured < fla * 0.70:
            note = (
                "Low vs FLA — light load, wrong scale, or open path; verify meter/clamp "
                "(approx)."
            )
        else:
            note = "Often near a common band vs FLA for many running compressors (approx)."
        notes.append(f"FLA {fla:.2f} A  delta {d:+.1f}%  —  {note}")
    if rla is not None:
        d = pct_diff(measured, rla)
        if measured > rla * 1.15:
            note = "High vs RLA — suspect load/airflow/charge/voltage/mechanical bind (approx)."
        elif measured < rla * 0.75:
            note = "Low vs RLA — may be unloaded or metering issue (approx)."
        else:
            note = "Often near a common band vs RLA while running (approx)."
        notes.append(f"RLA {rla:.2f} A  delta {d:+.1f}%  —  {note}")
    return notes


def voltage_imbalance_1ph(v1: float, v2: float) -> float:
    """Approximate percent imbalance for single-phase (two legs)."""
    avg = (v1 + v2) / 2.0
    if avg == 0:
        raise ValueError("Average voltage cannot be 0.")
    return abs(v1 - v2) / avg * 100.0


def voltage_imbalance_3ph(vab: float, vbc: float, vca: float) -> float:
    """NEMA-style percent voltage imbalance for three-phase."""
    avg = (vab + vbc + vca) / 3.0
    if avg == 0:
        raise ValueError("Average voltage cannot be 0.")
    max_dev = max(abs(vab - avg), abs(vbc - avg), abs(vca - avg))
    return max_dev / avg * 100.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Educational HVAC/R electrical helper")
    parser.add_argument("-i", "--interactive", action="store_true", help="Prompt for inputs")
    sub = parser.add_subparsers(dest="cmd")

    amps = sub.add_parser("amps", help="Compare measured amps to FLA/RLA")
    amps.add_argument("--measured", "--amps", dest="measured", type=float, required=True)
    amps.add_argument("--fla", type=float)
    amps.add_argument("--rla", type=float)

    imb = sub.add_parser("imbalance", help="Voltage imbalance")
    imb.add_argument("--v1", type=float, help="Leg 1 (1φ)")
    imb.add_argument("--v2", type=float, help="Leg 2 (1φ)")
    imb.add_argument("--vab", type=float)
    imb.add_argument("--vbc", type=float)
    imb.add_argument("--vca", type=float)
    return parser


def _interactive() -> argparse.Namespace:
    print(DISCLAIMER)
    print()
    ns = argparse.Namespace(
        cmd=prompt_choice("Check", ["amps", "imbalance"], "amps"),
        measured=None, fla=None, rla=None, v1=None, v2=None, vab=None, vbc=None, vca=None,
    )
    if ns.cmd == "amps":
        ns.measured = prompt_float("Measured amps")
        ns.fla = prompt_optional_float("FLA (blank to skip)")
        ns.rla = prompt_optional_float("RLA (blank to skip)")
    elif prompt_choice("Phase", ["1", "3"], "3") == "1":
        ns.v1 = prompt_float("Leg 1 volts")
        ns.v2 = prompt_float("Leg 2 volts")
    else:
        ns.vab = prompt_float("V A-B")
        ns.vbc = prompt_float("V B-C")
        ns.vca = prompt_float("V C-A")
    print()
    return ns


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.interactive:
        args = _interactive()
    elif not args.cmd:
        parser.error("a subcommand is required: amps or imbalance (or use -i)")
    print(DISCLAIMER)
    print(LOTO)
    print()

    try:
        if args.cmd == "amps":
            notes = amp_notes(args.measured, args.fla, args.rla)
            print(f"Measured: {args.measured:.2f} A")
            if notes:
                for n in notes:
                    print(n)
            else:
                print("Provide --fla and/or --rla from the nameplate.")
                return 1
        else:
            if args.v1 is not None and args.v2 is not None:
                pct = voltage_imbalance_1ph(args.v1, args.v2)
                print(f"1φ imbalance: {pct:.1f}%")
            elif None not in (args.vab, args.vbc, args.vca):
                pct = voltage_imbalance_3ph(args.vab, args.vbc, args.vca)
                print(f"3φ imbalance: {pct:.1f}%  (NEMA-style)")
                if pct > 2.0:
                    print("Above ~2% — check supply, connections, and load balance (approx).")
            else:
                print("Provide --v1/--v2 for 1φ or --vab/--vbc/--vca for 3φ.")
                return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
