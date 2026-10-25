"""Educational commercial cooler/freezer defrost & controls checklist (stdlib).

OEM controls vary — verify with equipment manuals and wiring diagrams.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from ._common import prompt_choice as pc

DISCLAIMER = (
    "EDUCATIONAL ONLY — OEM defrost controls vary widely. "
    "Verify every step against the equipment manual and wiring diagram."
)

BOX_TYPES = ("cooler", "freezer")
DEFROST_MODES = ("time-clock", "demand", "unknown")


def steps_for(box: str, mode: str) -> List[str]:
    box = box.lower()
    mode = mode.lower()
    steps = [
        "Lock out / tag out per site rules before opening panels",
        "Confirm box type setpoint and product load (cooler vs freezer)",
        "Identify defrost control: time clock, demand/adaptive, or OEM board",
        "Record scheduled defrost count/day and duration (or demand thresholds)",
        "Verify terminate device: probe / Klixon / pressure / timed failsafe",
        "Inspect evaporator coil frost pattern before forcing a defrost",
        "Force or wait for defrost; confirm compressor off / liquid line solenoid as designed",
        "Measure heater circuit voltage and amps vs nameplate during defrost",
        "Confirm drain pan heater (if equipped) and drain line clear / heat tape OK",
        "Check fan delay / drip time after terminate before fans restart",
        "After fans on: watch for water blow-off, uneven frost return, short-cycle",
        "Verify door heaters / frame heaters on freezers if icing at gasket",
        "Document pressures/temps and controller fault history before leaving",
    ]
    if mode == "time-clock":
        steps.insert(4, "Time clock: verify correct time-of-day, failsafe duration, and pin/program")
        steps.insert(5, "Confirm clock has power reserve / battery if applicable")
    elif mode == "demand":
        steps.insert(4, "Demand: confirm coil/air sensors seated and reading plausible temps")
        steps.insert(5, "Review adaptive parameters (max interval, terminate temp, lockouts)")
    if box == "freezer":
        steps.append("Freezer: confirm electric / hot-gas defrost type matches what you tested")
        steps.append("Check reverse-flow / hot-gas valves if hot-gas defrost (energize path)")
    else:
        steps.append("Cooler: off-cycle defrost may be normal — confirm heaters exist before condemning")
    return steps


def failure_notes(box: str, mode: str) -> List[str]:
    notes = [
        "Ice only on one end of coil → airflow / distribution / heater partial open",
        "Heaters open (0 A) or one element dead → high resistance / bad contactor / bad wire nut",
        "Defrost terminates too early → terminate probe in wrong place / shorted / too warm setpoint",
        "Never terminates → stuck relay, bad terminate, clock stuck in defrost, board fault",
        "Fans slam on wet coil → missing/failed fan delay; water on product / refreeze",
        "Drain freeze → clogged drain, failed pan heater, no heat tape, negative pressure pulling air",
        "Short defrost interval / iced coil again fast → door issues, humidity, low charge, bad TXV",
        "Controller in continuous defrost → config, failed sensor, or stuck demand logic",
    ]
    if mode == "time-clock":
        notes.append("Wrong time / DST / power blip → defrost during peak pull-down")
    if box == "freezer":
        notes.append("Door/frame heaters out → heavy perimeter ice mimicking coil problems")
    return notes


def format_report(box: str, mode: str) -> str:
    lines = [
        DISCLAIMER,
        "",
        f"Path: commercial {box} | defrost mode: {mode}",
        "",
        "Checklist:",
    ]
    for i, s in enumerate(steps_for(box, mode), 1):
        lines.append(f"  [ ] {i}. {s}")
    lines += ["", "Common failure notes:"]
    for n in failure_notes(box, mode):
        lines.append(f"  • {n}")
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational commercial defrost & controls checklist.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--box", choices=BOX_TYPES, help="cooler or freezer")
    p.add_argument("--mode", choices=DEFROST_MODES, help="time-clock, demand, or unknown")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    if ns.interactive:
        print(DISCLAIMER)
        print()
        box = pc("Box type", list(BOX_TYPES), "freezer")
        mode = pc("Defrost mode", list(DEFROST_MODES), "time-clock")
    else:
        if not ns.box or not ns.mode:
            print("Need --box and --mode (or -i)", file=sys.stderr)
            return 2
        box, mode = ns.box, ns.mode
    print(format_report(box, mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
