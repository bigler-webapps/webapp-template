from django_core_micha.auth.exception_handler import custom_exception_handler as _base_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def _is_error_object(d: dict) -> bool:
    """A leaf-error object has metadata keys AND no list values (DRF field-error dicts have list values)."""
    if not isinstance(d, dict):
        return False
    if any(isinstance(v, list) for v in d.values()):
        return False
    return any(k in d for k in ("code", "i18nKey", "message", "params"))


def _flatten(detail, field=None):
    out = []

    if isinstance(detail, dict):
        if _is_error_object(detail):
            out.append({
                "field": field,
                "code": str(detail.get("code", "error")),
                **({"message": str(detail.get("message"))} if detail.get("message") is not None else {}),
                **({"i18nKey": str(detail.get("i18nKey"))} if detail.get("i18nKey") is not None else {}),
                **({"params": detail.get("params")} if isinstance(detail.get("params"), dict) else {}),
            })
            return out

        for k, v in detail.items():
            nested_field = f"{field}.{k}" if field else k
            out.extend(_flatten(v, nested_field))
        return out

    if isinstance(detail, list):
        for item in detail:
            out.extend(_flatten(item, field))
        return out

    code = getattr(detail, "code", "error")
    out.append({
        "field": field,
        "code": str(code),
        "message": str(detail),
    })
    return out


def custom_exception_handler(exc, context):
    resp = drf_exception_handler(exc, context)
    if resp is None:
        return None

    if isinstance(exc, ValidationError):
        return Response({"errors": _flatten(resp.data)}, status=resp.status_code)

    return _base_handler(exc, context)
