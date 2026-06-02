"""
Permission Inventory Test.

Statischer Inventory-Check über alle URL-Patterns. Pro Endpoint werden die
effektiven `permission_classes` introspectiert. Vergleich gegen die
Public-Allowlist `PUBLIC_URL_NAMES`.

Hintergrund:
- `backend/settings.py` setzt `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`
  als belt-and-suspenders gegen künftige Type-B-Drifts.
- Dieser Test ist Regression-Guard: jede neue ViewSet/Action, die anonym
  erreichbar wird (direkt oder via Type-B-Fallback durch die DRF-Defaults),
  schlägt fehl.

Wenn der Test failt:
- "Unexpected anonymous endpoint": ein neuer Endpoint ist anonym, ohne
  in PUBLIC_URL_NAMES zu stehen. Entweder permission_classes ergänzen
  oder bewusst eintragen.
- "Listed but not anonymous": ein Eintrag in PUBLIC_URL_NAMES wird nicht
  mehr gefunden — Refactor hat den Endpoint geändert/entfernt.

Siehe auch: webapp-management/SECURITY_FINDINGS.md (S63, S66, S70) und
webapp-management/PLATFORM_PERMISSION_AUDIT.md.
"""
import pytest
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import AllowAny


# Hinweis:
# - Multi-Method @actions (z.B. `methods=['get','post']`) erzeugen mehrere
#   URLPatterns mit gleichem `name`; das Inventar-Dict überschreibt sich gegenseitig.
#   Solange GET- und POST-Permissions identisch sind, ist das unkritisch.
# - ViewSets mit custom `get_permissions()` OHNE `PUBLIC_ACTIONS`-Konvention
#   sind ein Blindspot. Neue Klassen mit custom `get_permissions()` müssen
#   entweder das `PUBLIC_ACTIONS`-Pattern adoptieren oder in
#   KNOWN_SAFE_CUSTOM_GET_PERMISSIONS gelistet werden.


# ---------------------------------------------------------------------------
# Public-Allowlist
# ---------------------------------------------------------------------------
# Endpoints, die anonym erreichbar sein DÜRFEN.
PUBLIC_URL_NAMES = frozenset({
    # ── django-core-micha Auth-Flow-Endpoints (designintendiert public) ───
    "access-code-validate",
    "password-reset-api",
    "recovery-request-recovery-login",
    "user-mfa-support-help",
    "user-register-confirm",
    "user-register-request",
    "user-reset-request",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _iter_url_patterns(patterns, prefix=""):
    """Recursively yield (full_pattern_str, URLPattern) tuples."""
    for p in patterns:
        if isinstance(p, URLResolver):
            new_prefix = prefix + str(p.pattern)
            yield from _iter_url_patterns(p.url_patterns, new_prefix)
        elif isinstance(p, URLPattern):
            yield prefix + str(p.pattern), p


def _classes_contain_allow_any(perm_classes):
    """
    True iff `perm_classes` contains `AllowAny` (or a subclass).

    `issubclass` statt Identity-Check, damit ein AllowAny-Subclass im Codebase
    ebenfalls erfasst wird.
    """
    if not perm_classes:
        return False
    return any(isinstance(p, type) and issubclass(p, AllowAny) for p in perm_classes)


def _extract_permission_classes(pattern):
    """
    Return the effective `permission_classes` list for the view behind
    this URLPattern, or None if introspection is not possible.

    Three sources, in priority order:
    1. `@action(permission_classes=[...])` decorator — DRF threads this into
       `callback.initkwargs["permission_classes"]`.
    2. Router-generated actions (list/retrieve/etc.) — check if action is in
       the ViewSet's `PUBLIC_ACTIONS` frozenset (Phase 4 convention); else
       fall back to class-level.
    3. APIView class-level `permission_classes`.

    Note: this does not generically simulate `get_permissions()` overrides;
    it only honours the `PUBLIC_ACTIONS`-pattern. Other custom
    `get_permissions()` impls are blind spots (false negatives — test is
    conservative).
    """
    cb = pattern.callback
    view_class = getattr(cb, "cls", None)
    if view_class is None:
        # Non-DRF view (e.g. plain Django view) — skip introspection.
        return None

    initkwargs = getattr(cb, "initkwargs", {}) or {}

    # 1. @action-decorator permission_classes — directly in initkwargs.
    if "permission_classes" in initkwargs:
        return initkwargs["permission_classes"]

    # 2. Router-generated actions (list/retrieve/create/update/...).
    #    DRF setzt `actions` direkt als Attribut am Callback (NICHT in
    #    initkwargs). Wenn eine der gemappten Actions in PUBLIC_ACTIONS ist,
    #    behandeln wir den Endpoint als public.
    actions_map = getattr(cb, "actions", None) or {}
    if actions_map:
        public_actions = getattr(view_class, "PUBLIC_ACTIONS", frozenset())
        for action_name in actions_map.values():
            if action_name in public_actions:
                return [AllowAny]
        return getattr(view_class, "permission_classes", None)

    # 3. APIView class-level.
    return getattr(view_class, "permission_classes", None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _collect_anonymous_endpoints():
    """Return {url_name: pattern_str} of all anonymously-reachable endpoints."""
    resolver = get_resolver()
    out = {}
    for full_pattern, p in _iter_url_patterns(resolver.url_patterns):
        perms = _extract_permission_classes(p)
        if _classes_contain_allow_any(perms):
            name = p.name or full_pattern
            out[name] = full_pattern
    return out


@pytest.fixture(scope="module")
def anonymous_endpoints():
    """Shared inventory — collected once, reused by all tests in this module."""
    return _collect_anonymous_endpoints()


def test_anonymous_endpoints_match_allowlist(anonymous_endpoints):
    """
    Asserts that the set of anonymously-reachable endpoints is exactly
    PUBLIC_URL_NAMES.

    Failure modes:
    - Unexpected public: a new endpoint silently became AllowAny — fix the
      permission_classes or add it to PUBLIC_URL_NAMES with rationale.
    - Missing from inventory: an entry in PUBLIC_URL_NAMES no longer matches —
      a refactor changed the URL name or removed the endpoint.
    """
    found_names = set(anonymous_endpoints.keys())

    unexpected_public = found_names - PUBLIC_URL_NAMES
    missing_from_inventory = PUBLIC_URL_NAMES - found_names

    msg_parts = []
    if unexpected_public:
        msg_parts.append(
            "Unexpected anonymously-reachable endpoints — add permission_classes "
            "or update PUBLIC_URL_NAMES with rationale:\n  "
            + "\n  ".join(sorted(
                f"{n}  →  {anonymous_endpoints[n]}"
                for n in unexpected_public
            ))
        )
    if missing_from_inventory:
        msg_parts.append(
            "Listed in PUBLIC_URL_NAMES but not found in URL resolver "
            "(refactor / rename / removal?):\n  "
            + "\n  ".join(sorted(missing_from_inventory))
        )

    # Hinweis: dieser Test sieht NUR Endpoints, deren AllowAny-Status via
    # Decorator, PUBLIC_ACTIONS-Konvention oder class-level permission_classes
    # erfasst wird. Custom `get_permissions()` ohne diese Konvention sind
    # blindspots — siehe Modul-Docstring und test_no_unaudited_custom_get_permissions.
    assert not msg_parts, "\n\n".join(msg_parts)


# ---------------------------------------------------------------------------
# Subclassing-Blindspot guard
# ---------------------------------------------------------------------------
# Bekannte sichere ViewSet-Klassen, die custom `get_permissions()` definieren,
# aber die `PUBLIC_ACTIONS`-Konvention NICHT verwenden — explizit auditiert.
# Neue Klassen mit custom `get_permissions()` müssen entweder das
# `PUBLIC_ACTIONS`-Pattern adoptieren oder hier mit Begründung gelistet werden.
# Add ViewSet classes that intentionally override get_permissions() here
KNOWN_SAFE_CUSTOM_GET_PERMISSIONS = frozenset({
    # django-core-micha.BaseUserViewSet — kombiniert class-level
    # [IsAuthenticated] mit per-action `@action(permission_classes=[AllowAny])`
    # für Signup/Reset/Recovery-Endpoints. Audit-bestätigt.
    "BaseUserViewSet",
    # django-core-micha.RecoveryRequestViewSet — recovery-login Action ist
    # bewusst public (Token-basiert). In PUBLIC_URL_NAMES verankert.
    "RecoveryRequestViewSet",
    # django-core-micha.AccessCodeViewSet — class-level
    # IsAccessCodeAdminOrSuperuser, custom get_permissions() returnt AllowAny
    # nur für `validate`-Action (in PUBLIC_URL_NAMES als access-code-validate).
    "AccessCodeViewSet",
})


def _has_class_level_get_permissions(view_class):
    """True if any class in MRO defines `get_permissions` directly (not inherited from APIView/GenericViewSet defaults)."""
    from rest_framework.views import APIView
    for cls in view_class.__mro__:
        if cls is APIView:
            break
        if "get_permissions" in cls.__dict__:
            return True
    return False


def test_no_unaudited_custom_get_permissions():
    """
    Subclassing-Blindspot-Guard. Any ViewSet with a custom `get_permissions()`
    (in its own class or anywhere in MRO above APIView) must either:
      - Use the `PUBLIC_ACTIONS` convention (detected via class attribute), OR
      - Appear on `KNOWN_SAFE_CUSTOM_GET_PERMISSIONS` (with an audit-comment).

    A new custom `get_permissions()` without either marker triggers this test
    and forces an explicit audit-trail entry.
    """
    resolver = get_resolver()
    flagged = {}
    for full_pattern, p in _iter_url_patterns(resolver.url_patterns):
        cb = p.callback
        view_class = getattr(cb, "cls", None)
        if view_class is None:
            continue
        if not _has_class_level_get_permissions(view_class):
            continue
        if hasattr(view_class, "PUBLIC_ACTIONS"):
            continue
        # Auch Basisklassen in der MRO prüfen.
        mro_names = {c.__name__ for c in view_class.__mro__}
        if mro_names & KNOWN_SAFE_CUSTOM_GET_PERMISSIONS:
            continue
        flagged[view_class.__name__] = full_pattern

    assert not flagged, (
        "ViewSets with custom get_permissions() but neither PUBLIC_ACTIONS "
        "nor entry in KNOWN_SAFE_CUSTOM_GET_PERMISSIONS — explicit audit needed:\n  "
        + "\n  ".join(sorted(f"{n}  →  {flagged[n]}" for n in flagged))
    )


def test_inventory_dump(anonymous_endpoints, capsys):
    """
    Diagnostic test: prints the full anonymous-endpoint inventory.

    Always passes. Run with `pytest -s` to inspect output. Useful when
    iterating on PUBLIC_URL_NAMES or after refactoring URL configs.
    """
    with capsys.disabled():
        print("\n=== Anonymous-reachable endpoint inventory ===")
        for name in sorted(anonymous_endpoints.keys()):
            print(f"  {name:<45}  {anonymous_endpoints[name]}")
        print(f"=== Total: {len(anonymous_endpoints)} ===\n")
