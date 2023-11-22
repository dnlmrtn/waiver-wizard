import json
import os
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        token_data = {
            "access_token": None,
            "consumer_key": os.environ.get('YAHOO_CONSUMER_KEY'),
            "consumer_secret": os.environ.get('YAHOO_CONSUMER_SECRET'),
            "guid": None,
            "refresh_token": None,
            "token_time": None,
            "token_type": "bearer"
        }
    
        with open('/app/core/api/token.json', 'w') as f:
            json.dump(token_data, f)
