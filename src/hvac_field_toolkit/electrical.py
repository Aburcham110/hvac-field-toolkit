"""Electrical field checks (FLA/RLA, capacitors, voltage imbalance)."""

from __future__ import annotations

import argparse
from typing import Optional

from . import DISCLAIMER

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
            note = "High vs FLA — check load, airflow, charge, voltage, and shorted windings (approx)."
        elif measured < fla * 0.70:
            note = "Low vs FLA — light load, wrong scale, or open path; verify meter/clamp (approx)."
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational HVAC/R electrical helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    amps = sub.add_parser("amps", help="Compare measured amps to FLA/RLA")
    amps.add_argument("--measured", type=float, required=True)
    amps.add_argument("--fla", type=float)
    amps.add_argument("--rla", type=float)

    imb = sub.add_parser("imbalance", help="Voltage imbalance")
    imb.add_argument("--v1", type=float, help="Leg 1 (1φ)")
    imb.add_argument("--v2", type=float, help="Leg 2 (1φ)")
    imb.add_argument("--vab", type=float)
    imb.add_argument("--vbc", type=float)
    imb.add_argument("--vca", type=float)

    args = parser.parse_args()
    print(DISCLAIMER)
    print(LOTO)
    print()

    if args.cmd == "amps":
        notes = amp_notes(args.measured, args.fla, args.rla)
        print(f"Measured: {args.measured:.2f} A")
        if notes:
            for n in notes:
                print(n)
        else:
            print("Provide --fla and/or --rla from the nameplate.")
    elif args.cmd == "imbalance":
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


if __name__ == "__main__":
    main()
