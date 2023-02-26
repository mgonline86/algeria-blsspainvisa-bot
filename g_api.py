"""Google API Class."""

from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GOOGLE():
    """Google API Class."""

    def __init__(self) -> None:
        """Oauth step."""
        self.creds = None
        self.auth()

    def auth(self):
        """Show basic usage of the Gmail API.

        Lists the user's Gmail labels.
        """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
    
    def list_labels(self) -> list:
        """List Labels."""
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
                return

            return labels

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')


    def list_messages(self) -> list:
        """List all labels in the user's mailbox."""
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(userId='me').execute()
            messages = results.get('messages', [])

            if not messages:
                print('No messages found.')
                return
            
            return messages

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')


    def get_message_by_id(self, id:str, format:str=None) -> dict:
        """Get the specified message."""
        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=self.creds)
            message = service.users().messages().get(userId='me', id=id, format=format).execute()

            if not message:
                print('No message found.')
                return

            return message

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')