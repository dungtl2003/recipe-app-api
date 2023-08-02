"""
Test custom Django management commands.
"""
# patch: mock behavior
# Psycopg2Error: one of the possible errors when trying to connect to db
# before the db is ready
# call_command: call commands by name
# OperationalError (from django):
# SimpleTestCase: no need for migration, just use simple
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# Using check function from base class to check states of db. Mocking this
# method allows us to simulate the respone.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    # Because we use patch decorater, so every method in here must have an
    # argument to catch the value (mock object). And we will use that object
    # to customize the behavior
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    # We mock sleep so that it will not make the system stops while testing.
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        # Here, the mock side effect is like an ordered list. The first 2 times
        # the mock is called, it will raise Psycopg2Error exeption. The next 3
        # times the mock is called, it will raise OperationalError exeption.
        # And the 6th time, it will return true.
        # Note that side effect will override return value from return_value if
        # side effect return a value. If you want to get return_value and not
        # side effect's return value, you can use unittest.mock.DEFAULT.
        # Normally, the database can have 3 stages: The first stage is when
        # the database's application has not even started yet, not ready for
        # any connection --> Psycopg2Error. After that, the application is
        # ready for connection, but it hasn't set up the testing database we
        # want to use, so Django will raise error --> OperationalError. After
        # that, it is ready --> True. 2 and 3 times are just try n error
        # experience, can change depending on cases.
        patched_check.side_effect = [Psycopg2Error] * 2 + \
                                    [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEquals(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
