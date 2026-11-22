"""Synthetic users owned by an isolated test-management run."""
import re
from importlib import import_module
from uuid import UUID

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models.deletion import Collector
from django_core_micha.test_management.activation import TestManagementError
from django_core_micha.test_management.protocol import AdapterAccountResult


# Replace these account templates and the managed-user fixture for your app.
TEMPLATES = ("supervisor", "collaborator")
ALLOWED_MODELS = {"auth.user", "users.userprofile", "account.emailaddress", "account.emailconfirmation"}
ALLOWED_FIELD_UPDATES = {("django_core_micha_auditlog.auditevent", "actor")}


def fail(code, message, status=400):
    raise TestManagementError(code, message, status)


class _Collector(Collector):
    def can_fast_delete(self, *args, **kwargs):
        return False


class TemplateTestManagementAdapter:
    def discovery(self):
        return {"templates": [{"name": name} for name in TEMPLATES],
                "supported_account_fields": ["username", "email", "name"],
                "supported_capabilities": [], "fixtures": ["managed-user"], "baseline_fields": {}}

    def start_run(self, *, run, baseline):
        if baseline:
            fail("invalid_baseline", "No baseline options are supported.")
        return {"users": {}, "fixtures": {}}

    def _save(self, run, state):
        run.adapter_state = state
        run.save(update_fields=["adapter_state", "updated_at"])

    @transaction.atomic
    def create_account(self, *, run, account_handle, payload):
        role = payload["template"]
        if role not in TEMPLATES:
            fail("unsupported_template", "Unknown template.")
        if payload.get("configuration"):
            fail("invalid_configuration", "Configuration is not supported.")
        identity = payload.get("synthetic_identity") or {}
        username = identity.get("username", "")
        if (not isinstance(username, str) or not re.fullmatch(r"(?:acc|tm|recovery)-[a-f0-9]{16}", username)
                or identity.get("email") != f"{username}@example.test"
                or set(identity) - {"username", "email", "name"}):
            fail("invalid_identity", "A synthetic example.test identity is required.")
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists() or User.objects.filter(email__iexact=identity["email"]).exists():
            fail("account_conflict", "Synthetic identity already exists.", 409)
        user = User.objects.create_user(username=username, email=identity["email"], password=payload["password"])
        user.profile.role = role
        user.profile.save(update_fields=["role"])
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        state = dict(run.adapter_state)
        state["users"] = {**state["users"], str(user.pk): username}
        self._save(run, state)
        return AdapterAccountResult(adapter_ref=str(user.pk), user_ref=str(user.pk), effective={"grants": [role], "role": role}, relationships={})

    def _owned_user(self, pk, username):
        user = get_user_model().objects.filter(pk=pk, username=username, email=f"{username}@example.test").first() if username else None
        if user is None:
            fail("account_not_found", "User ownership could not be verified.", 404)
        return user

    def _user(self, run, account):
        username = (run.adapter_state or {}).get("users", {}).get(str(account.user_ref))
        if not isinstance(username, str) or not re.fullmatch(r"(?:acc|tm|recovery)-[a-f0-9]{16}", username):
            fail("account_not_found", "Account marker is invalid.", 404)
        return self._owned_user(account.user_ref, username)

    def inspect_account(self, *, run, account):
        user = self._user(run, account)
        return {"grants": [user.profile.role], "role": user.profile.role, "relationships": {}}

    def update_account(self, *, run, account, payload):
        if set(payload) - {"password"}:
            fail("unsupported_update", "Only password updates are supported.")
        user = self._user(run, account)
        if "password" in payload:
            user.set_password(payload["password"])
            user.save(update_fields=["password"])
        return self.inspect_account(run=run, account=account)

    @transaction.atomic
    def prepare_fixture(self, *, run, fixture_handle, name, parameters):
        from django_core_micha.test_management.models import TestAccount
        if name != "managed-user" or set(parameters) != {"supervisor"}:
            fail("invalid_fixture", "A run-owned supervisor is required.")
        try:
            account = TestAccount.objects.get(run=run, handle=parameters["supervisor"], status=TestAccount.Status.ACTIVE, template="supervisor")
        except (TestAccount.DoesNotExist, ValueError, TypeError):
            fail("account_not_found", "The supervisor is not owned by this run.", 404)
        self._user(run, account)
        marker = f"tm-{run.handle.hex}-{UUID(fixture_handle).hex}"
        user = get_user_model().objects.create_user(username=marker, email=f"{marker}@example.test", password=None)
        state = dict(run.adapter_state)
        state["fixtures"] = {**state["fixtures"], str(user.pk): marker}
        self._save(run, state)
        return {"adapter_ref": fixture_handle, "user_id": user.pk, "username": marker}

    def _delete_user(self, user):
        collector = _Collector(using=user._state.db or "default")
        collector.collect([user])
        # Login writes audit events; deleting the user only clears their actor (SET_NULL), nothing else may change.
        # Django lists every SET_NULL field pointing at the user; only fields with real rows count.
        updated = {
            (field.model._meta.label_lower, field.name)
            for (field, _value), batches in collector.field_updates.items()
            if any(len(list(batch)) for batch in batches)
        }
        if {model._meta.label_lower for model in collector.data} - ALLOWED_MODELS or updated - ALLOWED_FIELD_UPDATES:
            fail("cleanup_failed", "User has unexpected related data.", 500)
        for session in Session.objects.all():
            try:
                matches = str(session.get_decoded().get("_auth_user_id", "")) == str(user.pk)
            except Exception as exc:
                raise TestManagementError("cleanup_failed", "Session inspection failed.", 500) from exc
            if matches:
                import_module(settings.SESSION_ENGINE).SessionStore(session_key=session.session_key).delete()
        user.delete()

    @transaction.atomic
    def delete_account(self, *, run, account):
        self._delete_user(self._user(run, account))
        state = dict(run.adapter_state)
        state["users"] = dict(state["users"])
        state["users"].pop(str(account.user_ref))
        self._save(run, state)

    @transaction.atomic
    def _cleanup(self, run):
        state = run.adapter_state or {}
        accounts = list(run.accounts.filter(status="active"))
        if {str(account.user_ref) for account in accounts} != set(state.get("users", {})):
            fail("cleanup_failed", "Account ownership state is inconsistent.", 500)
        for pk, marker in state.get("fixtures", {}).items():
            if not re.fullmatch(rf"tm-{run.handle.hex}-[a-f0-9]{{32}}", marker):
                fail("cleanup_failed", "Fixture marker is invalid.", 500)
            self._delete_user(self._owned_user(pk, marker))
        for account in accounts:
            self._delete_user(self._user(run, account))
        return {"removed": True}

    def close_run(self, *, run):
        return self._cleanup(run)

    def reset_run(self, *, run):
        result = self._cleanup(run)
        self._save(run, self.start_run(run=run, baseline=run.baseline))
        return result

    def recover_run(self, *, run):
        for account in run.accounts.filter(status="active"):
            self._user(run, account)
        for pk, marker in (run.adapter_state or {}).get("fixtures", {}).items():
            if not re.fullmatch(rf"tm-{run.handle.hex}-[a-f0-9]{{32}}", marker):
                fail("cleanup_failed", "Fixture marker is invalid.", 500)
            self._owned_user(pk, marker)
        return {"verified": True}
