from django.db import connection


def test_configured_database_driver_is_psycopg3():
    assert connection.vendor == "postgresql"
    assert connection.Database.__name__ == "psycopg"
