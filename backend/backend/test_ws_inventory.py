"""S112 WebSocket consumer inventory.

The template exposes exactly one consumer module -- the shared
`django_core_micha.notifications.consumers`, installed via dcm's settings_base --
and registers no WebSocket route of its own. Add every new consumer module to the
list below; an empty inventory is not the same as a secure one.
"""


def test_all_websocket_consumers_are_secure():
    from django_core_micha.auth.ws_permissions import assert_all_consumers_secure

    assert assert_all_consumers_secure(["django_core_micha.notifications.consumers"]) == []
