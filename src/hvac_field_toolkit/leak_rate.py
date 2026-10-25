"""Educational refrigerant leak-rate practice helper (stdlib only).

NOT a compliance system / NOT legal advice. Real AIM Act / 608 audits need
dedicated tools (e.g. 608Log-class workflows).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import List, Optional

from ._common import prompt_choice as pc
from ._common import prompt_float as pf

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
    "other",
)

# Leak-rate thresholds (%/yr) from eCFR 40 CFR 82.157(c)(2), checked 2026-10-25:
#   (i)   20 percent — commercial refrigeration equipment
#   (ii)  30 percent — industrial process refrigeration equipment
#   (iii) 10 percent — comfort cooling appliances or other appliances with a full
#         charge of 50 or more pounds not covered by (i) or (ii)
# The regulation has no separate "transport" category; transport/other appliances
# fall under (iii) -> "other". 82.157(a): since April 10, 2020 the section applies
# only to appliances with a full charge >= 50 lb of class I/class II (ODS, e.g.
# HCFC) refrigerant; HFC-only appliances are outside 82.157 (see EPA's AIM Act
# rules, 40 CFR part 84) — thresholds below are the same for every chem class.
THRESHOLDS = {
    # category: (hfc_pct, hcfc_pct, note)
    "comfort-cooling": (10.0, 10.0, "40 CFR 82.157(c)(2)(iii) comfort cooling"),
    "commercial-refrigeration": (20.0, 20.0, "40 CFR 82.157(c)(2)(i) commercial refrigeration"),
    "industrial": (30.0, 30.0, "40 CFR 82.157(c)(2)(ii) industrial process refrigeration"),
    "other": (10.0, 10.0, "40 CFR 82.157(c)(2)(iii) other appliances (incl. transport)"),
}

# Old category name kept as an accepted alias (no such category in 82.157).
CATEGORY_ALIASES = {"transport": "other"}

APPLICABILITY_NOTE = (
    "40 CFR 82.157 applies to appliances with a full charge of 50 lb or more of a "
    "class I / class II (ODS) refrigerant; HFC-only systems: check 40 CFR part 84."
)

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
    cat = CATEGORY_ALIASES.get(cat, cat)
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
        "Verify current EPA 40 CFR 82.157 / AIM Act (40 CFR part 84) applicability for this appliance",
    ]
    if over:
        reminders.insert(
            0, "Practice result OVER the 82.157 leak rate — treat as a drill to open real procedures"
        )
    else:
        reminders.insert(
            0, "Practice result within the 82.157 leak rate — still verify with official tools"
        )
    if full_charge_lbs < 50:
        reminders.insert(1, "Full charge under 50 lb — 40 CFR 82.157 leak-repair rules do not apply")
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
        f"Leak rate threshold (40 CFR 82.157(c)(2)): {r.threshold_pct:.0f}% / yr",
        f"Over threshold: {'YES' if r.over else 'no'}",
        APPLICABILITY_NOTE,
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
    p.add_argument(
        "--category",
        choices=CATEGORIES + tuple(CATEGORY_ALIASES),
        help="Appliance category ('transport' is accepted as an alias for 'other')",
    )
    p.add_argument("--chem", choices=CHEM_CLASSES, default="hfc")
    return p


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
