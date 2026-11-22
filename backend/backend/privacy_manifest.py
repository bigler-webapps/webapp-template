"""Privacy metadata; replace the template identity, controller and services for your app."""
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

LOCALES = ("de", "en", "fr")


def default_legal_reader_origin(env_type):
    return "https://bigler-consult.ch" if env_type == "production" else "https://staging.bigler-consult.ch"


def build_dcm_privacy(origin, session_cookie_name, csrf_cookie_name):
    try:
        parsed = urlsplit(origin)
        _ = parsed.port
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured("LEGAL_READER_ORIGIN must be an exact HTTPS origin.") from exc
    if not (parsed.hostname and (parsed.scheme == "https" or (parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"})) and not parsed.username and not parsed.password and not parsed.path and not parsed.query and not parsed.fragment and origin == f"{parsed.scheme}://{parsed.netloc}" and parsed.netloc == parsed.netloc.lower()):
        raise ImproperlyConfigured("LEGAL_READER_ORIGIN must be an exact HTTPS origin.")
    documents = {slug: {locale: f"{origin}/legal/{slug}?app=webapp-template&lang={locale if locale != 'fr' else 'en'}" for locale in LOCALES} for slug in ("privacy", "terms")}
    storage = [
        {"kind": "cookie", "name": name, "scope": "Host-only; path=/; SameSite=Lax.", "lifetime": lifetime}
        for name, lifetime in ((session_cookie_name, "Until sign-out or session expiry"), (csrf_cookie_name, "Up to one year"))
    ]
    storage.append({"kind": "localStorage", "name": "language", "scope": "This site's origin.", "lifetime": "Until cleared by the person"})
    return {
        "app": "webapp-template", "site": "webapp-template", "locales": list(LOCALES),
        "controller": {"name": "Template operator", "contact": f"{origin}/legal/privacy"},
        "notice": {"version": "2026-11-06", "documents": documents},
        "choice_validity_days": 180, "evidence_retention_days": 365,
        "purposes": [{
            "id": "necessary", "revision": 1, "required": True,
            "justification": "Protects sessions and requests and remembers the selected language.",
            "label": {"de": "Notwendig", "en": "Necessary", "fr": "Nécessaire"},
            "summary": {"de": "Schützt Anmeldung und Änderungen und merkt die gewählte Sprache.", "en": "Protects sign-in and changes and remembers the selected language.", "fr": "Protège la connexion et les modifications et mémorise la langue choisie."},
            "services": [{"id": "session-security", "provider": "Template operator, first-party", "trigger": "A session or protected request starts, or a person selects a language.", "data_categories": ["Session identifier", "CSRF token", "Selected language"], "recipients": ["Template operator"], "transfers": [], "browser_storage": storage, "server_retention": "Session records expire with the session; a signed-in language preference follows the profile."}],
            "withdrawal_clears": [],
        }],
    }
