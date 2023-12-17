import time
from django.db.utils import OperationalError
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        time.sleep(5)

        self.stdout.write(self.style.SUCCESS('Database available!'))
