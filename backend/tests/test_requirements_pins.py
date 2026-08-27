"""
Requirements-Pin-Guard.

`requirements.txt` darf nicht zurück zu unbeschränkten Einträgen driften:
jede neue Abhängigkeit braucht mindestens eine `>=`-Untergrenze (oder ein
exaktes `==`/VCS-Tag). Ein Eintrag ohne jede Versionsangabe zieht bei
`pip install` unbemerkt die jeweils neueste Version — ein Breaking-Change
in einer Dependency würde erst beim nächsten Deploy auffallen, nicht im
Diff.
"""
import re
from pathlib import Path

REQUIREMENTS_PATH = Path(__file__).resolve().parents[1] / "requirements.txt"

# Ein VCS-Pin (z.B. `paket @ git+https://...@<tag>`) ist per Definition auf
# einen unveränderlichen Tag/Commit fixiert und daher von der `>=`/`==`-Pflicht
# ausgenommen.
_VCS_PIN_RE = re.compile(r"@\s*git\+.+@[^\s]+$")
_VERSION_SPECIFIER_RE = re.compile(r"(==|>=|<=|~=|!=|>|<)")


def _requirement_lines():
    lines = []
    for raw_line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def test_requirements_txt_has_no_unconstrained_entry():
    unconstrained = [
        line
        for line in _requirement_lines()
        if not _VERSION_SPECIFIER_RE.search(line) and not _VCS_PIN_RE.search(line)
    ]
    assert not unconstrained, (
        "requirements.txt entries with no version constraint (add a `>=` floor "
        "at minimum): " + ", ".join(unconstrained)
    )
