import time
import requests
import os
# initialise globals
LAST_KEY_TIME = 0
LAST_TOKEN = None

AUTH_URL = 'https://api.services.mimecast.com/oauth/token'

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def get_bearer_token(auth_url=AUTH_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    """Fetch a fresh bearer token from the auth server."""
    print("Requesting new bearer token")
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    resp = requests.post(auth_url, data=auth_data)
    resp.raise_for_status()
    return resp.json()['access_token']

def get_current_epoch():
    """Returns the current epoch time in seconds."""
    return int(time.time())

def is_within_age(past_epoch, age=1800):
    """
    Checks if the given epoch timestamp is within the last `age*0.9` seconds.
    """
    return (get_current_epoch() - past_epoch) < age*0.90

def return_auth_key():
    """
    Returns a valid bearer token, only fetching a new one if
    the existing token is older than 30 minutes.
    """
    global LAST_KEY_TIME, LAST_TOKEN

    if LAST_TOKEN is None or not is_within_age(LAST_KEY_TIME):
        # need to fetch a fresh token
        LAST_TOKEN = get_bearer_token()
        LAST_KEY_TIME = get_current_epoch()
    else:
        print("Reusing existing bearer token")

    return LAST_TOKEN

if __name__ == "__main__":
    # simple loop to demonstrate
    while True:
        token = return_auth_key()
        print("Bearer:", token)
        time.sleep(3)
