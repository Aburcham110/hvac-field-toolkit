"""Shared disclaimer text and interactive input helpers for the toolkit CLIs."""

from __future__ import annotations

from typing import Optional, Sequence

DISCLAIMER = (
    "EDUCATIONAL ONLY — verify with OEM literature, a calibrated instrument, "
    "and your AHJ. Not for final equipment selection or live electrical work."
)


def prompt_float(prompt: str, default: Optional[float] = None) -> float:
    """Prompt until a number is entered; blank returns ``default`` when given."""
    while True:
        suf = f" [{default}]" if default is not None else ""
        s = input(f"{prompt}{suf}: ").strip()
        if not s and default is not None:
            return float(default)
        try:
            return float(s)
        except ValueError:
            print("Enter a number.")


def prompt_optional_float(prompt: str, default: Optional[float] = None) -> Optional[float]:
    """Like :func:`prompt_float` but blank with no default returns ``None``."""
    while True:
        suf = f" [{default}]" if default is not None else ""
        raw = input(f"{prompt}{suf}: ").strip()
        if not raw and default is not None:
            return float(default)
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            print("Enter a number.")


def prompt_choice(label: str, choices: Sequence[str], default: str) -> str:
    """Prompt until one of ``choices`` is entered (exact match); blank = default."""
    while True:
        s = input(f"{label} ({'/'.join(choices)}) [{default}]: ").strip() or default
        if s in choices:
            return s
        print("Invalid choice.")


def prompt_text(label: str, default: str = "") -> str:
    """Free-text prompt; blank returns ``default``."""
    suf = f" [{default}]" if default else ""
    s = input(f"{label}{suf}: ").strip()
    return s or default
