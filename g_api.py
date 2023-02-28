"""Google API Class."""

import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
    ]


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

    def send_message(self, to:str, subject:str, _message:str, _from:str=None) -> dict:
        """Create and send an email message
        Print the returned  message id
        Returns: Message object, including message id"""

        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = EmailMessage()

            message.set_content(_message)

            message['To'] = to
            message['Subject'] = subject
            if _from:
                message['From'] = _from

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Sent Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message