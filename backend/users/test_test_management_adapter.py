from uuid import uuid4

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

if not apps.is_installed("django_core_micha.test_management"):
    pytest.skip("Requires dedicated test-management settings.", allow_module_level=True)

from allauth.account.models import EmailAddress
from django.contrib.sessions.models import Session
from django_core_micha.test_management.activation import TestManagementError
from django_core_micha.test_management.models import TestAccount, TestInstance, TestRun
from rest_framework.test import APIClient
from .test_management import TemplateTestManagementAdapter


class AdapterTests(TestCase):
    def setUp(self):
        self.adapter = TemplateTestManagementAdapter()
        instance = TestInstance.objects.create(controller_token_digest="x", expires_at=timezone.now())
        self.run = TestRun.objects.create(instance=instance, idempotency_key="run")
        self.run.adapter_state = self.adapter.start_run(run=self.run, baseline={})
        self.run.save()

    def account(self, role, index):
        username = f"tm-{index:016x}"
        result = self.adapter.create_account(run=self.run, account_handle=str(uuid4()), payload={
            "template": role, "synthetic_identity": {"username": username, "email": f"{username}@example.test"},
            "password": "synthetic-password",
        })
        account = TestAccount.objects.create(run=self.run, idempotency_key=f"{role}-{index}", template=role,
                                             adapter_ref=result.adapter_ref, user_ref=result.user_ref)
        return account, result

    def fixture(self, account):
        return self.adapter.prepare_fixture(run=self.run, fixture_handle=str(uuid4()), name="managed-user",
                                            parameters={"supervisor": str(account.handle)})

    def test_templates_and_fixture_validate_ownership(self):
        self.assertEqual({item["name"] for item in self.adapter.discovery()["templates"]}, {"supervisor", "collaborator"})
        for index, role in enumerate(("supervisor", "collaborator"), 1):
            account, result = self.account(role, index)
            self.assertEqual(result.effective["role"], role)
            self.assertEqual(self.adapter.inspect_account(run=self.run, account=account)["role"], role)
            if role == "supervisor":
                supervisor = account
            else:
                with self.assertRaises(TestManagementError):
                    self.fixture(account)
        fixture = self.fixture(supervisor)
        user = get_user_model().objects.get(pk=fixture["user_id"])
        self.assertEqual(user.profile.role, "none")
        self.assertIn(self.run.handle.hex, user.username)
        self.assertEqual(self.run.adapter_state["fixtures"][str(user.pk)], user.username)
        with self.assertRaises(TestManagementError):
            self.adapter.start_run(run=self.run, baseline={"unexpected": True})
        with self.assertRaises(TestManagementError):
            self.adapter.create_account(run=self.run, account_handle=str(uuid4()), payload={"template": "supervisor", "configuration": {"role": "admin"}})

    def test_cleanup_preserves_every_sentinel_row_and_session(self):
        User = get_user_model()
        sentinel = User.objects.create_user(username="ordinary-user", email="ordinary@example.test", password="password")
        email = EmailAddress.objects.create(user=sentinel, email=sentinel.email, verified=True, primary=True)
        self.client.force_login(sentinel)
        sentinel_session = self.client.session.session_key
        rows = [sentinel, sentinel.profile, email]
        snapshots = [(type(row), row.pk, type(row).objects.filter(pk=row.pk).values().get()) for row in rows]
        for index, cleanup in enumerate((self.adapter.reset_run, self.adapter.close_run), 1):
            account, result = self.account("supervisor", index)
            fixture = self.fixture(account)
            owned = User.objects.get(pk=result.user_ref)
            owned_profile = owned.profile.pk
            owned_email = EmailAddress.objects.get(user=owned).pk
            fixture_profile = User.objects.get(pk=fixture["user_id"]).profile.pk
            clients = [Client(), Client()]
            clients[0].force_login(owned)
            clients[1].force_login(User.objects.get(pk=fixture["user_id"]))
            session_keys = [client.session.session_key for client in clients]
            cleanup(run=self.run)
            self.assertFalse(User.objects.filter(pk__in=[result.user_ref, fixture["user_id"]]).exists())
            self.assertFalse(type(sentinel.profile).objects.filter(pk__in=[owned_profile, fixture_profile]).exists())
            self.assertFalse(EmailAddress.objects.filter(pk=owned_email).exists())
            self.assertFalse(Session.objects.filter(session_key__in=session_keys).exists())
            for model, pk, snapshot in snapshots:
                self.assertEqual(model.objects.filter(pk=pk).values().get(), snapshot)
            self.assertTrue(Session.objects.filter(session_key=sentinel_session).exists())
            account.status = TestAccount.Status.DELETED
            account.save(update_fields=["status"])

    def test_collaborator_cannot_change_fixture_role(self):
        supervisor, _ = self.account("supervisor", 1)
        collaborator, result = self.account("collaborator", 2)
        fixture = self.fixture(supervisor)
        User = get_user_model()
        user = User.objects.get(pk=fixture["user_id"])
        before = User.objects.filter(pk=user.pk).values().get()
        profile_before = type(user.profile).objects.filter(pk=user.profile.pk).values().get()
        client = APIClient()
        client.force_authenticate(User.objects.get(pk=supervisor.user_ref))
        self.assertEqual(client.get(f"/api/users/{user.pk}/").status_code, 200)
        client.force_authenticate(User.objects.get(pk=result.user_ref))
        response = client.patch(f"/api/users/{user.pk}/update-role/", {"role": "collaborator"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(User.objects.filter(pk=user.pk).values().get(), before)
        self.assertEqual(type(user.profile).objects.filter(pk=user.profile.pk).values().get(), profile_before)

    def test_cleanup_fails_closed_on_changed_marker(self):
        account, _ = self.account("supervisor", 1)
        fixture = self.fixture(account)
        user = get_user_model().objects.get(pk=fixture["user_id"])
        user.username = "ordinary-user"
        user.save(update_fields=["username"])
        with self.assertRaises(TestManagementError):
            self.adapter.close_run(run=self.run)
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=account.user_ref).exists())
