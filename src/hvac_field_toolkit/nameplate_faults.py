"""Educational nameplate capture + starter fault-code stubs (stdlib only).

Incomplete database — verify every code with the OEM manual.
Service Tech chat can also use photos for nameplates.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DISCLAIMER = (
    "EDUCATIONAL ONLY — fault-code database is incomplete / stubbed. "
    "Verify with the OEM service manual. Photos of nameplates can be reviewed in Service Tech chat."
)

DEFAULT_STORE = Path.home() / ".hvac_nameplate_faults.json"

# brand -> code -> {meaning, causes[], parts[], tools[]}
FAULT_DB: Dict[str, Dict[str, dict]] = {
    "generic": {
        "E1": {
            "meaning": "Sensor / thermistor fault (generic stub)",
            "causes": ["Open/shorted sensor", "Loose plug", "Board input failed"],
            "parts": ["Thermistor", "Harness"],
            "tools": ["Multimeter", "OEM sensor chart"],
        },
        "E2": {
            "meaning": "High pressure / high limit (generic stub)",
            "causes": ["Dirty condenser", "Failed fan", "Overcharge", "Non-condensables"],
            "parts": ["Condenser fan motor", "HP switch"],
            "tools": ["Manifold", "Amp clamp"],
        },
        "E3": {
            "meaning": "Low pressure / loss of charge (generic stub)",
            "causes": ["Leak", "Restriction", "Failed LP switch"],
            "parts": ["LP switch", "Drier"],
            "tools": ["Leak detector", "Nitrogen", "Micron gauge"],
        },
        "LO": {
            "meaning": "Lockout after retries (generic stub)",
            "causes": ["Repeated flame/pressure failures", "Soft lock needing reset"],
            "parts": ["Igniter", "Pressure switch", "Control board"],
            "tools": ["Manometer", "Multimeter"],
        },
    },
    "carrier": {
        "33": {
            "meaning": "Carrier-style communication / board fault (educational stub)",
            "causes": ["Comm wiring", "Failed control", "Power brownout"],
            "parts": ["Control board", "Comm harness"],
            "tools": ["Multimeter", "OEM flowchart"],
        },
        "41": {
            "meaning": "Blower motor fault (educational stub)",
            "causes": ["ECM module", "Seized blower", "High static"],
            "parts": ["Blower motor/module"],
            "tools": ["Static pressure probes", "Amp clamp"],
        },
    },
    "trane": {
        "E.172": {
            "meaning": "Trane-style outdoor fault stub (educational)",
            "causes": ["OD fan", "Inverter", "Sensor"],
            "parts": ["OD fan", "Inverter board"],
            "tools": ["OEM service facts", "Multimeter"],
        },
    },
    "rheem": {
        "L6": {
            "meaning": "Rheem-style pressure switch stub (educational)",
            "causes": ["Blocked vent", "Bad pressure switch", "Inducer"],
            "parts": ["Pressure switch", "Inducer"],
            "tools": ["Manometer"],
        },
    },
    "copeland": {
        "1": {
            "meaning": "Copeland Comfort Alert — long run / low capacity stub",
            "causes": ["Low charge", "TXV", "Dirty filter"],
            "parts": ["TXV", "Filter-drier"],
            "tools": ["Manifold", "Clamp meter"],
        },
        "5": {
            "meaning": "Comfort Alert — open circuit (compressor/wiring) stub",
            "causes": ["Open winding", "Contactor", "Broken wire"],
            "parts": ["Contactor", "Compressor"],
            "tools": ["Megger", "Multimeter"],
        },
    },
}


@dataclass
class Nameplate:
    brand: str = ""
    model: str = ""
    serial: str = ""
    voltage: str = ""
    refrigerant: str = ""
    charge_lbs: str = ""
    notes: str = ""
    fault_code: str = ""


def normalize_brand(b: str) -> str:
    return b.strip().lower().replace(" ", "")


def lookup_fault(brand: str, code: str) -> List[Tuple[str, dict]]:
    """Return list of (source_brand, entry) matches, preferred brand first then generic."""
    code_key = code.strip()
    code_u = code_key.upper()
    hits: List[Tuple[str, dict]] = []
    b = normalize_brand(brand)
    for source in (b, "generic"):
        table = FAULT_DB.get(source, {})
        for k, v in table.items():
            if k.upper() == code_u or k == code_key:
                hits.append((source, v))
                break
    return hits


def format_card(np: Nameplate, hits: List[Tuple[str, dict]]) -> str:
    lines = [
        DISCLAIMER,
        "",
        "Equipment card:",
        f"  Brand: {np.brand or '—'}",
        f"  Model: {np.model or '—'}",
        f"  Serial: {np.serial or '—'}",
        f"  Voltage: {np.voltage or '—'}",
        f"  Refrigerant: {np.refrigerant or '—'}",
        f"  Charge: {np.charge_lbs or '—'}",
        f"  Fault / blink: {np.fault_code or '—'}",
    ]
    if np.notes:
        lines.append(f"  Notes: {np.notes}")
    if np.fault_code:
        lines.append("")
        if not hits:
            lines.append(f"No stub match for code {np.fault_code!r}. Check OEM manual.")
            lines.append("Likely next: photograph nameplate + board LED chart; ask Service Tech chat.")
        else:
            for source, entry in hits:
                lines.append(f"Stub match ({source}): {entry['meaning']}")
                lines.append("  Ranked likely causes:")
                for i, c in enumerate(entry.get("causes", []), 1):
                    lines.append(f"    {i}. {c}")
                parts = ", ".join(entry.get("parts", []) or ["—"])
                tools = ", ".join(entry.get("tools", []) or ["—"])
                lines.append(f"  Parts to consider: {parts}")
                lines.append(f"  Tools: {tools}")
    lines += [
        "",
        "Tip: Service Tech chat can use nameplate photos for field transcription.",
        "",
        DISCLAIMER,
    ]
    return "\n".join(lines)


def load_store(path: Path) -> List[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_card(path: Path, np: Nameplate) -> None:
    rows = load_store(path)
    rows.append(asdict(np))
    path.write_text(json.dumps(rows, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Educational nameplate + fault-code stub helper.",
        epilog=DISCLAIMER,
    )
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--brand")
    p.add_argument("--model")
    p.add_argument("--serial")
    p.add_argument("--voltage")
    p.add_argument("--refrigerant")
    p.add_argument("--charge")
    p.add_argument("--notes")
    p.add_argument("--code", help="Fault code or blink pattern text")
    p.add_argument("--save", action="store_true", help="Append card to local JSON store")
    p.add_argument("--store", default=str(DEFAULT_STORE), help="JSON store path")
    p.add_argument("--list-codes", action="store_true", help="List stub codes and exit")
    return p


def prompt(label: str, default: str = "") -> str:
    suf = f" [{default}]" if default else ""
    s = input(f"{label}{suf}: ").strip()
    return s or default


def from_interactive() -> Nameplate:
    print(DISCLAIMER)
    print()
    return Nameplate(
        brand=prompt("Brand"),
        model=prompt("Model"),
        serial=prompt("Serial"),
        voltage=prompt("Voltage"),
        refrigerant=prompt("Refrigerant"),
        charge_lbs=prompt("Charge (lbs)"),
        fault_code=prompt("Fault code / blink"),
        notes=prompt("Notes"),
    )


def main(argv: Optional[List[str]] = None) -> int:
    ns = build_parser().parse_args(argv)
    if ns.list_codes:
        print(DISCLAIMER)
        print()
        for brand, table in FAULT_DB.items():
            print(f"[{brand}]")
            for code, entry in table.items():
                print(f"  {code}: {entry['meaning']}")
        return 0

    if ns.interactive:
        np = from_interactive()
    else:
        np = Nameplate(
            brand=ns.brand or "",
            model=ns.model or "",
            serial=ns.serial or "",
            voltage=ns.voltage or "",
            refrigerant=ns.refrigerant or "",
            charge_lbs=ns.charge or "",
            notes=ns.notes or "",
            fault_code=ns.code or "",
        )
        if not any([np.brand, np.model, np.fault_code]):
            print("Provide nameplate fields and/or --code (or -i / --list-codes)", file=sys.stderr)
            return 2

    hits = lookup_fault(np.brand, np.fault_code) if np.fault_code else []
    print(format_card(np, hits))
    if ns.save:
        path = Path(ns.store).expanduser()
        save_card(path, np)
        print(f"\nSaved card to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
