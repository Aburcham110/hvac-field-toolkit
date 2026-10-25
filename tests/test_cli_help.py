"""Every hvac-* console script in pyproject must render --help (exit 0, nonempty).

Guards against argparse format errors such as an unescaped "%" in help text.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _console_scripts():
    text = PYPROJECT.read_text(encoding="utf-8")
    section = re.search(r"^\[project\.scripts\]\s*\n(.*?)(?=^\[|\Z)", text, re.S | re.M)
    assert section, "no [project.scripts] section in pyproject.toml"
    return re.findall(r'^(hvac-[\w-]+)\s*=\s*"([\w.]+):(\w+)"', section.group(1), re.M)


SCRIPTS = _console_scripts()


def test_expected_script_count():
    assert len(SCRIPTS) == 17


@pytest.mark.parametrize("name, module, func", SCRIPTS, ids=[s[0] for s in SCRIPTS])
def test_console_script_help(name, module, func):
    code = (
        "import sys; sys.argv = [{!r}, '--help']; "
        "from {} import {} as f; sys.exit(f())"
    ).format(name, module, func)
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip(), f"{name} --help printed nothing"
    assert "usage:" in res.stdout
