from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from xml.etree import ElementTree as ET

from core.models import Players

from core.api.yahoo import YahooFantasyAPIService

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

from django.http import HttpResponse, HttpResponseRedirect
import requests
from urllib.parse import urlencode

YEAR = '2023'

file_path = '/app/core/api/token.json'

import json


def home(request):
    # Your client ID and secret, replace with actual values
    CLIENT_ID = 'dj0yJmk9UzhXcWV6TEdCOHR1JmQ9WVdrOVpsSjRSV052YzFFbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTU5'
    CLIENT_SECRET = 'ad1b0243136881fda85e78f18acc8cb305a5f836'
    REDIRECT_URI = 'https://e980-70-31-173-131.ngrok-free.app/home/'
    AUTH_URL = 'https://api.login.yahoo.com/oauth2/request_auth'
    TOKEN_URL = 'https://api.login.yahoo.com/oauth2/get_token'
    LEAGUES_URL = 'https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games/leagues'  # Yahoo Fantasy Sports API endpoint for leagues
    
    if 'yahoo_oauth_key' in request.session:
        token = request.session['yahoo_oauth_key']
    
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(LEAGUES_URL, headers=headers)
        
        if response.status_code == 200 and response.text.strip():
            root = ET.fromstring(response.text)
            
            # Extracting leagues
            leagues = []
            for league in root.findall(".//league"):
                league_data = {}
                for child in league:
                    league_data[child.tag] = child.text
                leagues.append(league_data)
            
            # Do something with the leagues, e.g., render it in a template
            return HttpResponse(leagues)
            
        else:
            return HttpResponse(f"Failed to fetch leagues: {response.status_code}")
        
    else:
        if 'code' in request.GET:
            # Step 3: Fetch Token using the code
            auth_code = request.GET['code']
            payload = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'code': auth_code,
                'grant_type': 'authorization_code'
            }
            response = requests.post(TOKEN_URL, data=payload)
            token_data = response.json()
            request.session['yahoo_oauth_key'] = token_data['access_token']
            
            # Redirect back to the same view to proceed with fetching leagues
            return HttpResponseRedirect(REDIRECT_URI)
        
        else:
            # Step 1: Redirect user to Yahoo's OAuth2 authorization page
            params = {
                'client_id': CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code',
                'scope': 'openid',  # or other scopes you need
            }
            auth_url = f"{AUTH_URL}?{urlencode(params)}"
            return HttpResponseRedirect(auth_url)



def login(request):
    yfa = YahooFantasyAPIService()
    leagues = yfa.get_leagues()
    
    return HttpResponse(leagues)
