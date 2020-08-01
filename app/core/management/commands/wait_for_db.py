import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available
    """

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                # try and set db connection
                db_conn = connections['default']
            except OperationalError:
                # output msg
                self.stdout.write('Database unavailable, waiting 1 second...')
                # wait for 1 sec and try again
                time.sleep(1)
        # style.SUCCESS wraps it in a green output
        self.stdout.write(self.style.SUCCESS('Database available!'))
