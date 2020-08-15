import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow


ROOT = os.path.abspath(os.getcwd())


class OAuth:
    def __init__(self):
        if not os.path.exists(os.path.join(ROOT, 'oauth/credentials.dat')):
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(ROOT, 'oauth/client_secrets.json'),
                                                             scopes=['https://www.googleapis.com/auth/contacts'])
            self.__credentials = flow.run_console()

            with open(os.path.join(ROOT, 'oauth/credentials.dat'), 'wb') as credentials_dat:
                pickle.dump(self.credentials, credentials_dat)
        else:
            with open(os.path.join(ROOT, 'oauth/credentials.dat'), 'rb') as credentials_dat:
                self.__credentials = pickle.load(credentials_dat)

    @property
    def credentials(self):
        return self.__credentials
