"""Basic psychrometric helpers (educational approximations)."""

from __future__ import annotations

import argparse
import math

from . import DISCLAIMER


def approx_wet_bulb(db: float, rh: float) -> float:
    """Rough wet-bulb estimate from dry-bulb (°F) and relative humidity (%).

    Educational approximation only — not a full psychrometric chart.
    """
    if not (0 <= rh <= 100):
        raise ValueError("RH must be 0–100")
    # Simple depression model; good enough for field practice ranges
    depression = (100 - rh) * 0.15 * (db / 70.0)
    return db - depression


def delta_t_airflow_note(supply: float, return_t: float, expected_dt: float = 18.0) -> str:
    """Educational note on measured vs expected temperature drop."""
    dt = return_t - supply
    if dt < expected_dt * 0.7:
        return f"Low ΔT ({dt:.1f}°F) — check airflow, charge, or metering (approx)."
    if dt > expected_dt * 1.3:
        return f"High ΔT ({dt:.1f}°F) — possible low airflow or restriction (approx)."
    return f"ΔT {dt:.1f}°F often near a common band for many systems (approx)."


def main() -> None:
    parser = argparse.ArgumentParser(description="Educational psychrometrics helper")
    parser.add_argument("--db", type=float, required=True, help="Dry-bulb °F")
    parser.add_argument("--rh", type=float, help="Relative humidity %")
    parser.add_argument("--wb", type=float, help="Wet-bulb °F (optional)")
    args = parser.parse_args()

    print(DISCLAIMER)
    print(f"Dry-bulb: {args.db:.1f} °F")
    if args.rh is not None:
        wb_est = approx_wet_bulb(args.db, args.rh)
        print(f"Approx wet-bulb from {args.rh:.0f}% RH: {wb_est:.1f} °F")
    if args.wb is not None:
        print(f"Given wet-bulb: {args.wb:.1f} °F")


if __name__ == "__main__":
    main()
