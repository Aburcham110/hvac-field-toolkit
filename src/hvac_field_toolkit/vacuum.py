"""Educational vacuum / evacuation coach (stdlib only).

Not a substitute for a calibrated micron gauge or OEM evacuation procedures.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from ._common import prompt_choice as pc

DISCLAIMER = (
    "EDUCATIONAL ONLY — not a substitute for a calibrated digital micron gauge "
    "or OEM evacuation / dehydration procedures."
)

MODES = ("coach", "interpret-decay", "pre-charge")


def coach_lines() -> List[str]:
    return [
        "Use a digital MICRON gauge on the system — compound manifold inches are not microns",
        "Manifold can show '29+ inHg' while the system is still thousands of microns wet",
        "Educational target: pull below 500 microns (many OEM specs 250–500; follow OEM)",
        "Place micron gauge on the system, preferably far from the pump (opposite port / core)",
        "Remove Schrader cores with core tools for conductance; use short large-diameter hoses",
        "Fresh vacuum pump oil; gas ballast briefly if pump design allows, then close",
        "Isolate pump with core tool / valve and watch HOLD — do not read while pump is still open",
        "Blank-off the gauge on itself first to prove the gauge and hose are tight",
        "Nitrogen sweep / triple evac when OEM or contamination calls for it",
        "Never use the micron gauge as a permanent system sensor through charging abuse",
    ]


def interpret_decay(start_micron: float, after_min: float, minutes: float) -> List[str]:
    if minutes <= 0:
        raise ValueError("minutes must be > 0")
    if start_micron < 0 or after_min < 0:
        raise ValueError("microns must be >= 0")
    rise = after_min - start_micron
    rate = rise / minutes
    lines = [
        f"Hold test: {start_micron:.0f} → {after_min:.0f} microns over {minutes:.1f} min "
        f"(Δ {rise:+.0f}, ~{rate:.0f} µ/min)",
        "",
        "Educational interpretation (not a leak certificate):",
    ]
    if rise <= 50 and after_min <= 500:
        lines.append("  • Small/no rise near target — often acceptable hold (verify OEM)")
    elif rise > 0 and rate < 50 and after_min < 1000:
        lines.append("  • Slow rise — often outgassing / residual moisture; continue evacuate or heat")
    elif rate >= 50 and rate < 200:
        lines.append("  • Moderate rise — moisture or small leak; nitrogen test / longer pull / heat")
    else:
        lines.append("  • Fast rise — suspect leak, open core, wet system, or gauge/hose leak")
    lines += [
        "  • Moisture: rise that slows as you re-pull and heat the evaporator",
        "  • Leak: rise that continues toward atmosphere; fails standing nitrogen pressure test",
        "  • Outgassing: plastic/elastomer / oil vapors — improves with time under vacuum",
        "  • Always blank-off gauge to rule out the instrument before condemning the system",
    ]
    return lines


def pre_charge() -> List[str]:
    return [
        "Micron target met and hold/decay acceptable per OEM",
        "Pump isolated; gauge still on system for final check",
        "Cores reinstalled / torqued; new seals if required",
        "Weigh-in charge ready; cylinder ID matches nameplate refrigerant",
        "No pressure-only top-off plan for zeotropic blends",
        "Break vacuum with refrigerant vapor/liquid only as OEM specifies (not air)",
        "Document microns, hold time, and charge lbs in job notes",
    ]


def format_report(mode: str, start: Optional[float], after: Optional[float], minutes: Optional[float]) -> str:
    lines = [DISCLAIMER, "", f"Mode: {mode}", ""]
    if mode == "coach":
        lines.append("Evacuation coach:")
        for i, s in enumerate(coach_lines(), 1):
            lines.append(f"  {i}. {s}")
    elif mode == "interpret-decay":
        if start is None or after is None or minutes is None:
            raise ValueError("interpret-decay needs --start-micron --after-micron --minutes")
        for s in interpret_decay(start, after, minutes):
            lines.append(s)
    else:
        lines.append("Checklist before charge:")
        for i, s in enumerate(pre_charge(), 1):
            lines.append(f"  [ ] {i}. {s}")
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational vacuum / evacuation coach.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--mode", choices=MODES, default="coach")
    p.add_argument("--start-micron", type=float)
    p.add_argument("--after-micron", type=float)
    p.add_argument("--minutes", type=float, help="Hold duration minutes")
    return p


def pf(prompt: str) -> float:
    while True:
        try:
            return float(input(f"{prompt}: ").strip())
        except ValueError:
            print("Enter a number.")


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    try:
        if ns.interactive:
            print(DISCLAIMER)
            print()
            mode = pc("Mode", list(MODES), "coach")
            start = after = minutes = None
            if mode == "interpret-decay":
                start = pf("Start microns (after isolate)")
                after = pf("Microns after hold")
                minutes = pf("Hold minutes")
        else:
            mode = ns.mode
            start, after, minutes = ns.start_micron, ns.after_micron, ns.minutes
        print(format_report(mode, start, after, minutes))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
