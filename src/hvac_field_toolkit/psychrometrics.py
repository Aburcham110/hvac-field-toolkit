"""Basic psychrometric helpers (educational approximations)."""

from __future__ import annotations

import argparse
import math
import sys
from typing import List, Optional

from ._common import DISCLAIMER, prompt_float, prompt_optional_float


def approx_wet_bulb(db: float, rh: float) -> float:
    """Wet-bulb estimate (°F) from dry-bulb (°F) and relative humidity (%).

    Uses Stull (2011), "Wet-Bulb Temperature from Relative Humidity and Air
    Temperature", J. Appl. Meteor. Climatol. 50:2267-2269. The formula is in
    °C, so dry-bulb is converted °F -> °C and the result converted back.

    Validity (per Stull): roughly 5-99% RH and -20 to 50 °C (-4 to 122 °F),
    near sea-level pressure (~14.7 psia). Typical error is within about
    ±0.3 °C (~0.5 °F) inside that range; outside it, treat results with caution.
    At 100% RH, wet-bulb equals dry-bulb and that value is returned directly.

    Educational approximation only — not a substitute for a psychrometer,
    full psychrometric chart, or OEM tools.
    """
    if not (0 <= rh <= 100):
        raise ValueError("RH must be 0–100")
    if rh >= 100:
        return float(db)
    t = (db - 32.0) / 1.8
    tw = (
        t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(t + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * rh ** 1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )
    return min(tw * 1.8 + 32.0, float(db))


def delta_t_airflow_note(supply: float, return_t: float, expected_dt: float = 18.0) -> str:
    """Educational note on measured vs expected temperature drop."""
    dt = return_t - supply
    if dt < expected_dt * 0.7:
        return f"Low ΔT ({dt:.1f}°F) — check airflow, charge, or metering (approx)."
    if dt > expected_dt * 1.3:
        return f"High ΔT ({dt:.1f}°F) — possible low airflow or restriction (approx)."
    return f"ΔT {dt:.1f}°F often near a common band for many systems (approx)."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Educational psychrometrics helper")
    parser.add_argument("-i", "--interactive", action="store_true", help="Prompt for inputs")
    parser.add_argument("--db", "--dry-bulb", dest="db", type=float, help="Dry-bulb °F")
    parser.add_argument("--rh", type=float, help="Relative humidity %%")
    parser.add_argument("--wb", "--wet-bulb", dest="wb", type=float,
                        help="Wet-bulb °F (optional)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.interactive:
        print(DISCLAIMER)
        print()
        args.db = prompt_float("Dry-bulb °F")
        args.rh = prompt_optional_float("Relative humidity % (blank to skip)")
        args.wb = prompt_optional_float("Wet-bulb °F (blank to skip)")
        print()
    elif args.db is None:
        parser.error("the following arguments are required: --db (or use -i)")

    print(DISCLAIMER)
    print(f"Dry-bulb: {args.db:.1f} °F")
    try:
        if args.rh is not None:
            wb_est = approx_wet_bulb(args.db, args.rh)
            print(f"Approx wet-bulb from {args.rh:.0f}% RH: {wb_est:.1f} °F")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if args.wb is not None:
        print(f"Given wet-bulb: {args.wb:.1f} °F")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
