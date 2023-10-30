import json
import os

def write_token_file():
    token_data = {
        "access_token": os.environ.get('YAHOO_ACCESS_TOKEN'),
        "consumer_key": os.environ.get('YAHOO_CONSUMER_KEY'),
        "consumer_secret": os.environ.get('YAHOO_CONSUMER_SECRET'),
        "guid": null,
        "refresh_token": os.environ.get('YAHOO_REFRESH_TOKEN'),
        "token_time": 1698375522.160845,
        "token_type": "bearer"
    }

    with open('/app/core/api/token.json', 'w') as f:
        json.dump(token_data, f)

if __name__ == "__main__":
    write_token_file()