"""User API tests for the generic BaseUserViewSet routes (dcm >= 2.44.1).

A non-admin user is scoped to their own row. On the generic detail route they may
only PATCH the allowlisted profile fields (`current_patch_allowed_fields`, widened
by the template with `is_new`) and may not delete their own row.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="member@example.com",
        email="member@example.com",
        password="not-used-force-authenticated",
    )


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


def _detail_url(user):
    return f"/api/users/{user.pk}/"


@pytest.mark.django_db
def test_non_admin_can_patch_allowlisted_is_new_on_own_row(client, user):
    user.profile.is_new = True
    user.profile.save()

    response = client.patch(_detail_url(user), {"is_new": False}, format="json")

    assert response.status_code == 200, response.content
    user.profile.refresh_from_db()
    assert user.profile.is_new is False


@pytest.mark.django_db
def test_non_admin_cannot_patch_non_allowlisted_field_on_own_row(client, user):
    response = client.patch(_detail_url(user), {"is_active": False}, format="json")

    # dcm 2.44.x refuses a disallowed field on the generic route with a
    # validation error naming it (400, via _enforce_safe_profile_fields).
    assert response.status_code == 400, response.content
    assert "is_active" in str(response.json())
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_non_admin_cannot_delete_own_row(client, user):
    response = client.delete(_detail_url(user))

    assert response.status_code == 403, response.content
    assert User.objects.filter(pk=user.pk).exists()
