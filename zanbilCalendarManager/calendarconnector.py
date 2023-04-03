from __future__ import print_function

import datetime
import os.path
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from allauth.socialaccount.models import SocialToken


# from manageevents import addEvent, busyEvent, releaseEvent


def zanbilServiceBuilder():
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'profile', 'email']
    creds = None
    SERVICE_ACCOUNT_FILE = "./staticfiles/serviceAccountCredentials.json"
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print('An error occurred: %s' % error)


def clientServiceBuilder(request):
    access_token = SocialToken.objects.get(
        account__user=request.user, account__provider='google')
    creds = Credentials(token=access_token.token,
                        refresh_token=access_token.token_secret,
                        client_id=access_token.app.client_id,
                        client_secret=access_token.app.secret)
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service

    except HttpError as error:
        print('An error occurred: %s' % error)
