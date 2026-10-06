"""INF-61: every backend dependency is pinned exactly (`==`).

An unpinned or floored name resolves the newest release on every build, unreviewed. That is how the
estate's S244 rate-limit regression and the 2026-08-20 Celery Beat outage happened (a bare name walked
BACKWARDS to a 2020 release when a cap elsewhere made the newest one unsatisfiable, and the deploy
reported success). A stale exact pin is at least visible, and it only stays fresh while Renovate or
a person moves it.

Three guards:

1. `test_every_requirement_is_pinned_exactly` -- scans every `requirements*.txt` next to `manage.py`
   (plus whatever they include with `-r`/`-c`) and fails on any line that is not an exact pin.
2. The mutation proofs -- the SAME scan (`_requirement_files` + `_offenders`) run against broken
   copies written to a temporary directory: a bare name, a floor, a wildcard, a URL and an include
   chain. A guard that has never been shown to fail on a broken copy is decoration.
3. `test_pins_match_installed_versions` -- each pin equals what this image actually installs, i.e.
   the pins are the image's versions and not a bump in disguise.
"""
import re
from importlib import metadata
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

BACKEND = next(p for p in Path(__file__).resolve().parents if (p / "manage.py").exists())

# A VCS requirement is pinned when it names an immutable ref: a release tag (vX.Y.Z, X.Y.Z, optionally
# an rc/a/b suffix) or a full commit SHA. The estate pins shared packages by tag (AGENTS.md: every
# consumer pins by tag, never a branch).
_PINNED_VCS = re.compile(r"^git\+https://[^@\s]+@(v?\d+(\.\d+){1,3}(-?(rc|a|b)\d+)?|[0-9a-f]{40})$")
_INCLUDE = re.compile(r"^(?:-r|--requirement|-c|--constraint)[\s=]+(\S+)$")


def _is_pinned_vcs(req: Requirement) -> bool:
    return bool(req.url) and bool(_PINNED_VCS.match(req.url))


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def _requirement_files(root: Path) -> list[Path]:
    """`requirements*.txt` directly under `root` (the generated requirements.lock.txt is never
    hand-edited and carries hashes), plus every file they include, followed recursively."""
    found: list[Path] = []
    queue = sorted(p for p in root.glob("requirements*.txt") if p.name != "requirements.lock.txt")
    while queue:
        path = queue.pop(0)
        if path in found:
            continue
        found.append(path)
        for raw in _lines(path):
            m = _INCLUDE.match(raw.split("#", 1)[0].strip())
            if m and (path.parent / m.group(1)).is_file():
                queue.append((path.parent / m.group(1)).resolve())
    return found


def _unpinned(lines: list[str]) -> list[str]:
    """Requirement lines that are not an exact `==` pin. Comments, blanks and `-r`/`-c` includes are
    skipped here (the includes are followed by `_requirement_files`); any other option line, a URL
    requirement without an immutable ref, and a wildcard pin (`==1.*`) all count as unpinned."""
    bad = []
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line or _INCLUDE.match(line):
            continue
        if line.startswith("-"):
            bad.append(line)
            continue
        try:
            req = Requirement(line)
        except InvalidRequirement:
            bad.append(line)
            continue
        if req.url:
            if not _is_pinned_vcs(req):
                bad.append(line)
            continue
        specs = list(req.specifier)
        if len(specs) != 1 or specs[0].operator != "==" or specs[0].version.endswith(".*"):
            bad.append(line)
    return bad


def _offenders(paths: list[Path]) -> dict[str, list[str]]:
    return {p.name: bad for p in paths if (bad := _unpinned(_lines(p)))}


REQUIREMENT_FILES = _requirement_files(BACKEND)


def test_requirement_files_were_found():
    """Otherwise the guard below would pass on an empty list."""
    assert any(p.name == "requirements.txt" for p in REQUIREMENT_FILES), f"no requirements.txt next to {BACKEND / 'manage.py'}"


def test_every_requirement_is_pinned_exactly():
    offenders = _offenders(REQUIREMENT_FILES)
    assert offenders == {}, (
        f"requirement line(s) that are not an exact `==` pin: {offenders}. An unpinned or floored "
        "dependency resolves the newest release on every build, unreviewed (INF-61). Pin it at the "
        "version the image installs; Renovate moves it from there."
    )


def test_guard_flags_every_kind_of_loose_requirement():
    """Mutation check on the line parser: if this fails, `_unpinned` cannot tell a loose line from a
    pinned one."""
    for loose in (
        "requests", "requests>=2.0", "requests~=2.0", "requests==2.*", "requests>=2.0,<3", "django-allauth[mfa]",
        "pkg @ https://example.invalid/pkg.whl", "pkg @ git+https://example.invalid/pkg.git@main",
        "pkg @ git+https://example.invalid/pkg.git", "pkg @ git+https://example.invalid/pkg.git@2.10.0main", "-e ./local",
    ):
        assert _unpinned([loose]) == [loose], loose


def test_guard_accepts_exact_pins_comments_markers_and_includes():
    assert _unpinned(["requests==2.34.2", "django-allauth[mfa]==65.19.7  # why", "# only a comment", "", "   "]) == []
    assert _unpinned(['pywin32==306 ; sys_platform == "win32"', "-r requirements.txt", "-c constraints.txt"]) == []
    assert _unpinned(["pkg @ git+https://example.invalid/pkg.git@v2.10.0", "pkg @ git+https://example.invalid/pkg.git@2.10.0"]) == []
    assert _unpinned(["pkg @ git+https://example.invalid/pkg.git@" + "a" * 40]) == []


def test_scan_finds_and_flags_loose_lines_in_broken_copies(tmp_path):
    """The mutation proof the order asks for, on the real code path: the exact scan the guard runs
    (`_requirement_files` then `_offenders`) against a broken copy of a backend directory, including
    a loose line hidden behind an include chain."""
    (tmp_path / "manage.py").write_text("")
    (tmp_path / "requirements.txt").write_text("django==6.1.1\nsome-new-dependency\n-r extra/more.txt\n")
    (tmp_path / "requirements-test.txt").write_text("-r requirements.txt\npytest>=8.0\n")
    (tmp_path / "extra").mkdir()
    (tmp_path / "extra" / "more.txt").write_text("hidden-dependency~=1.0\n")
    (tmp_path / "requirements.lock.txt").write_text("loose-but-generated\n")
    files = _requirement_files(tmp_path)
    assert sorted(p.name for p in files) == ["more.txt", "requirements-test.txt", "requirements.txt"]
    assert _offenders(files) == {
        "requirements.txt": ["some-new-dependency"],
        "requirements-test.txt": ["pytest>=8.0"],
        "more.txt": ["hidden-dependency~=1.0"],
    }


def test_scan_passes_a_clean_copy(tmp_path):
    (tmp_path / "manage.py").write_text("")
    (tmp_path / "requirements.txt").write_text("# c\ndjango==6.1.1\nrequests==2.34.2  # why\n")
    (tmp_path / "requirements-test.txt").write_text("-r requirements.txt\npytest==9.1.1\n")
    assert _offenders(_requirement_files(tmp_path)) == {}


def test_pins_match_installed_versions():
    """No-op check: each exact pin equals the version this image installs. A package that is not
    installed here, or whose marker does not apply, is not checked, but at least one pin must have
    been checked or the test proves nothing."""
    mismatched, checked = [], 0
    for path in REQUIREMENT_FILES:
        for raw in _lines(path):
            line = raw.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            req = Requirement(line)
            if req.url or (req.marker is not None and not req.marker.evaluate()):
                continue
            specs = list(req.specifier)
            if len(specs) != 1 or specs[0].operator != "==":
                continue  # not an exact pin: test_every_requirement_is_pinned_exactly reports it
            try:
                installed = metadata.version(canonicalize_name(req.name))
            except metadata.PackageNotFoundError:
                continue
            checked += 1
            if installed != specs[0].version:
                mismatched.append((path.name, req.name, specs[0].version, installed))
    assert checked > 0, "no pinned package is installed in this environment: the no-op check verified nothing"
    assert mismatched == [], (
        f"pin differs from the installed version (file, package, pinned, installed): {mismatched}. "
        "A pin that moves a version is a bump, not INF-61's no-op; re-measure the image."
    )
