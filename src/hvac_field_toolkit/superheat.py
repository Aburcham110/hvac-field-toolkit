"""Superheat & subcooling calculations (educational PT tables)."""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Tuple

from . import DISCLAIMER

# Compact educational PT tables: (psig, Tsat °F)
# Approximate mid-range values. Real work needs manufacturer charts or a
# refrigerant-rated digital manifold. Zeotropic blends use a single mid-glide curve.
PT_TABLES: Dict[str, List[Tuple[float, float]]] = {
    "R-410A": [
        (50, -20), (70, -5), (80, 2), (90, 8), (100, 14), (110, 19), (118, 23),
        (125, 26), (130, 28), (140, 33), (150, 37), (160, 41), (170, 45),
        (180, 48), (190, 52), (200, 55), (210, 58), (220, 61), (230, 64),
        (240, 67), (250, 70), (260, 72), (270, 75), (280, 77), (290, 80),
        (300, 82), (320, 87), (340, 91), (360, 95), (380, 99), (400, 103),
        (420, 106), (440, 110), (460, 113), (480, 116), (500, 119),
    ],
    "R-22": [
        (20, -20), (30, -5), (35, 2), (40, 8), (45, 13), (49, 16), (55, 22),
        (60, 26), (65, 30), (70, 33), (75, 37), (80, 40), (85, 43), (90, 46),
        (95, 49), (100, 52), (105, 54), (110, 57), (120, 62), (130, 66),
        (140, 70), (150, 74), (160, 78), (170, 81), (180, 84), (190, 87),
        (200, 90), (210, 93), (220, 96), (230, 98), (240, 101), (250, 104),
        (260, 106), (270, 109), (280, 111), (300, 116),
    ],
    "R-134a": [
        (10, -10), (15, 0), (20, 8), (25, 15), (30, 22), (35, 28), (40, 34),
        (45, 39), (50, 44), (55, 48), (60, 52), (70, 60), (80, 66), (90, 72),
        (100, 78), (110, 83), (120, 88), (130, 93), (140, 97), (150, 101),
        (160, 105), (180, 112), (200, 119),
    ],
    "R-404A": [
        (20, -25), (30, -12), (40, -2), (50, 7), (60, 14), (70, 21), (80, 27),
        (90, 32), (100, 37), (110, 42), (120, 46), (130, 50), (140, 54),
        (150, 58), (160, 61), (180, 68), (200, 74), (220, 80), (240, 85),
        (260, 90), (280, 95), (300, 99),
    ],
    "R-407C": [
        (30, -10), (40, 0), (50, 8), (60, 15), (70, 22), (80, 28), (90, 33),
        (100, 38), (110, 43), (120, 47), (140, 55), (160, 62), (180, 69),
        (200, 75), (220, 80), (240, 85), (260, 90), (280, 95), (300, 99),
        (320, 103),
    ],
    "R-32": [
        (50, -15), (70, 0), (90, 10), (110, 19), (130, 27), (150, 34),
        (170, 40), (190, 46), (210, 51), (230, 56), (250, 61), (270, 65),
        (290, 69), (310, 73), (330, 77), (350, 80), (380, 86), (400, 89),
        (450, 97), (500, 105),
    ],
    "R-454B": [
        (50, -18), (70, -3), (90, 8), (110, 17), (130, 25), (150, 32),
        (170, 38), (190, 44), (210, 49), (230, 54), (250, 59), (270, 63),
        (290, 67), (310, 71), (330, 75), (350, 78), (380, 84), (400, 87),
        (450, 95), (500, 102),
    ],
}

REFRIGERANTS = sorted(PT_TABLES.keys())


def sat_temp(refrigerant: str, psig: float) -> float:
    """Return approximate saturation temperature (°F) at the given pressure."""
    table = PT_TABLES.get(refrigerant)
    if not table:
        raise ValueError(f"Unsupported refrigerant: {refrigerant}")
    if psig < table[0][0] or psig > table[-1][0]:
        raise ValueError(
            f"Pressure {psig} psig outside table "
            f"({table[0][0]}–{table[-1][0]}) for {refrigerant}"
        )
    for i in range(len(table) - 1):
        p0, t0 = table[i]
        p1, t1 = table[i + 1]
        if p0 <= psig <= p1:
            if p1 == p0:
                return t0
            return t0 + ((psig - p0) / (p1 - p0)) * (t1 - t0)
    return table[-1][1]


def superheat(refrigerant: str, suction_psig: float, suction_line_temp: float) -> float:
    """Superheat (°F) = suction line temp − saturation temp at suction pressure."""
    return suction_line_temp - sat_temp(refrigerant, suction_psig)


def subcooling(refrigerant: str, liquid_psig: float, liquid_line_temp: float) -> float:
    """Subcooling (°F) = saturation temp at liquid pressure − liquid line temp."""
    return sat_temp(refrigerant, liquid_psig) - liquid_line_temp


def sh_guide(sh: float) -> str:
    if sh < 5:
        return "Very low — risk of liquid floodback (approx)."
    if sh <= 20:
        return "Often in a common target band for many fixed-orifice systems (approx)."
    if sh <= 30:
        return "Somewhat high — may indicate undercharge or airflow issue (approx)."
    return "High — check charge, metering device, and airflow (approx)."


def sc_guide(sc: float) -> str:
    if sc < 5:
        return "Low — possible undercharge or restriction (approx)."
    if sc <= 15:
        return "Often in a common target band for many TXV systems (approx)."
    if sc <= 20:
        return "Somewhat high — may indicate overcharge (approx)."
    return "High — check for overcharge or non-condensables (approx)."


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Educational HVAC/R superheat & subcooling calculator"
    )
    parser.add_argument("--refrigerant", "-r", choices=REFRIGERANTS, required=True)
    parser.add_argument("--suction-psig", type=float, help="Suction pressure (psig)")
    parser.add_argument("--suction-temp", type=float, help="Suction line temperature (°F)")
    parser.add_argument("--liquid-psig", type=float, help="Liquid pressure (psig)")
    parser.add_argument("--liquid-temp", type=float, help="Liquid line temperature (°F)")
    args = parser.parse_args()

    print(DISCLAIMER)
    print(f"Refrigerant: {args.refrigerant}")
    print("Note: Saturation temps from compact educational PT table.\n")

    if args.suction_psig is not None and args.suction_temp is not None:
        sh = superheat(args.refrigerant, args.suction_psig, args.suction_temp)
        print(f"Superheat: {sh:.1f} °F  —  {sh_guide(sh)}")
    if args.liquid_psig is not None and args.liquid_temp is not None:
        sc = subcooling(args.refrigerant, args.liquid_psig, args.liquid_temp)
        print(f"Subcooling: {sc:.1f} °F  —  {sc_guide(sc)}")
    if (args.suction_psig is None or args.suction_temp is None) and (
        args.liquid_psig is None or args.liquid_temp is None
    ):
        print("Provide suction and/or liquid pressure + line temperature.")
        sys.exit(1)


if __name__ == "__main__":
    main()
