"""Educational refrigerant leak-rate practice helper (stdlib only).

NOT a compliance system / NOT legal advice. Real AIM Act / 608 audits need
dedicated tools (e.g. 608Log-class workflows).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import List, Optional

BANNER = (
    "!!! NOT A COMPLIANCE SYSTEM — NOT LEGAL ADVICE !!!\n"
    "Educational practice only. Real AIM Act / Section 608 leak-rate audits\n"
    "require dedicated recordkeeping tools and current regulatory thresholds."
)

DISCLAIMER = BANNER

CATEGORIES = (
    "comfort-cooling",
    "commercial-refrigeration",
    "industrial",
    "transport",
)

# Educational threshold presets (%/yr). Labeled approximate / historical-ish bands.
# HFC-ish vs HCFC-ish columns for practice — NOT current law.
THRESHOLDS = {
    # category: (hfc_pct, hcfc_pct, note)
    "comfort-cooling": (10.0, 10.0, "comfort cooling practice band"),
    "commercial-refrigeration": (20.0, 35.0, "commercial refrigeration practice band"),
    "industrial": (30.0, 35.0, "industrial process practice band"),
    "transport": (50.0, 50.0, "transport refrigeration practice band"),
}

CHEM_CLASSES = ("hfc", "hcfc", "other")


@dataclass
class Result:
    full_charge_lbs: float
    added_lbs: float
    days: float
    category: str
    chem: str
    annualized_pct: float
    threshold_pct: float
    over: bool
    reminders: List[str]


def annualized_leak_pct(full_charge_lbs: float, added_lbs: float, days: float) -> float:
    if full_charge_lbs <= 0:
        raise ValueError("full charge must be > 0")
    if days <= 0:
        raise ValueError("period days must be > 0")
    if added_lbs < 0:
        raise ValueError("added lbs must be >= 0")
    # (added / full) * (365 / days) * 100
    return (added_lbs / full_charge_lbs) * (365.0 / days) * 100.0


def analyze(
    *,
    full_charge_lbs: float,
    added_lbs: float,
    days: float,
    category: str,
    chem: str = "hfc",
) -> Result:
    cat = category.strip().lower()
    if cat not in CATEGORIES:
        raise ValueError(f"Unknown category: {category!r}")
    ch = chem.strip().lower()
    if ch not in CHEM_CLASSES:
        raise ValueError(f"Unknown chem class: {chem!r}")
    hfc_t, hcfc_t, _note = THRESHOLDS[cat]
    thr = hcfc_t if ch == "hcfc" else hfc_t
    pct = annualized_leak_pct(full_charge_lbs, added_lbs, days)
    over = pct > thr
    reminders = [
        "Confirm full charge from nameplate / OEM data plate (not a guess)",
        "Use only refrigerant actually added to this appliance over the period",
        "Exclude initial charge after install if your practice rules say so",
        "Calendar the next inspection / leak repair follow-up if over threshold",
        "Log dates, lbs, and tech ID in your official compliance system — not this tool",
        "Verify current EPA AIM Act / 608 thresholds; presets here are educational only",
    ]
    if over:
        reminders.insert(0, "Practice result OVER educational band — treat as a drill to open real procedures")
    else:
        reminders.insert(0, "Practice result within educational band — still verify with official tools")
    return Result(
        full_charge_lbs=full_charge_lbs,
        added_lbs=added_lbs,
        days=days,
        category=cat,
        chem=ch,
        annualized_pct=pct,
        threshold_pct=thr,
        over=over,
        reminders=reminders,
    )


def format_report(r: Result) -> str:
    lines = [
        BANNER,
        "",
        f"Category: {r.category}  |  Chem class: {r.chem}",
        f"Full charge: {r.full_charge_lbs:.2f} lb",
        f"Added over period: {r.added_lbs:.2f} lb in {r.days:.1f} days",
        f"Annualized leak rate (practice): {r.annualized_pct:.1f}% / yr",
        f"Educational threshold preset: {r.threshold_pct:.0f}% / yr",
        f"Over educational band: {'YES' if r.over else 'no'}",
        "",
        "Next-step reminders:",
    ]
    for i, m in enumerate(r.reminders, 1):
        lines.append(f"  {i}. {m}")
    lines += ["", BANNER]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational leak-rate practice helper (NOT compliance).",
        epilog=DISCLAIMER,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--full-charge-lbs", type=float)
    p.add_argument("--added-lbs", type=float)
    p.add_argument("--days", type=float, help="Rolling period length in days")
    p.add_argument("--category", choices=CATEGORIES)
    p.add_argument("--chem", choices=CHEM_CLASSES, default="hfc")
    return p


def pf(prompt: str, default: Optional[float] = None) -> float:
    while True:
        suf = f" [{default}]" if default is not None else ""
        s = input(f"{prompt}{suf}: ").strip()
        if not s and default is not None:
            return float(default)
        try:
            return float(s)
        except ValueError:
            print("Enter a number.")


def pc(label: str, choices: List[str], default: str) -> str:
    while True:
        s = (input(f"{label} ({'/'.join(choices)}) [{default}]: ").strip() or default)
        if s in choices:
            return s
        print("Invalid choice.")


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    try:
        if ns.interactive:
            print(BANNER)
            print()
            full = pf("Full charge (lb)")
            added = pf("Refrigerant added over period (lb)")
            days = pf("Period length (days)", 365.0)
            cat = pc("System category", list(CATEGORIES), "commercial-refrigeration")
            chem = pc("Chem class", list(CHEM_CLASSES), "hfc")
            r = analyze(
                full_charge_lbs=full,
                added_lbs=added,
                days=days,
                category=cat,
                chem=chem,
            )
        else:
            need = [ns.full_charge_lbs, ns.added_lbs, ns.days, ns.category]
            if any(v is None for v in need):
                raise SystemExit(
                    "Need --full-charge-lbs --added-lbs --days --category (or -i)"
                )
            r = analyze(
                full_charge_lbs=ns.full_charge_lbs,
                added_lbs=ns.added_lbs,
                days=ns.days,
                category=ns.category,
                chem=ns.chem,
            )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(format_report(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
