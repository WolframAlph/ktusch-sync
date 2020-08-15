import os

from requests import Session, Response, exceptions as http_exceptions
from google.auth.transport.requests import Request

from business.sync.auth import OAuth
from business.apis import Google


def status_hook(response: Response, *args, **kwargs):
    response.raise_for_status()

    return response


class AuthHttpSession(Session):

    def __init__(self, client):
        super().__init__()

        if issubclass(client.__class__, Google):
            self.credentials = OAuth().credentials
            self.update_token()
        else:
            self.credentials = None
            self.params.update({'hapikey': os.getenv('HUBSPOT_API_KEY')})
            self.headers.update({'Content-Type': 'application/json'})

        self.hooks.update({'response': status_hook})

    def update_token(self):
        self.headers.update({'Authorization': "Bearer " + self.credentials.token})

    def request(self, *args, **kwargs):
        if self.credentials is not None and self.credentials.expired:
            self.credentials.refresh(Request())
            self.update_token()
        return super().request(*args, **kwargs)
