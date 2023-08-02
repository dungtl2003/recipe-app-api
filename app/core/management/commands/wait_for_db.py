"""
Django command to wait for database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg2Error

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database...')
        db_up = False
        max_tries = 7
        tried = 1
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError) as e:
                if tried > max_tries:
                    self.stdout.write(self.style.ERROR('Connection failed!'))
                    raise e
                self.stdout.write(f'Database unavailable, attempting to reconnect ({tried})')
                time.sleep(1)
                tried += 1

        self.stdout.write(self.style.SUCCESS('Database available!'))
