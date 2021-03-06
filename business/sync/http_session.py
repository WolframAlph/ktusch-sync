from functools import wraps
import logging
from time import sleep

from requests import Session, Response, exceptions as http_exceptions

from business.rest.statuses import HTTP


def status_hook(response: Response, *args, **kwargs):
    response.raise_for_status()
    return response


def retry_on_status(retries, statuses):

    def decorated(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            nonlocal retries

            try:
                return method(self, *args, **kwargs)
            except http_exceptions.HTTPError as e:
                if e.response.status_code in statuses and retries:
                    logging.info(f"Failed to perform request with error message: {str(e)}")
                    retry_after = e.response.headers.get('Retry-After')

                    if not retry_after:
                        logging.info('No Rery-After header was provided, sleeping for 1 minute')
                        sleep(60)
                    else:
                        logging.info(f"Required to sleep for {retry_after} seconds, sleeping...")
                        sleep(retry_after)

                    retries -= 1
                    return wrapper(self, *args, **kwargs)
                else:
                    print(f"Failed to obtain response with error message: {str(e)}")
                    raise
        return wrapper

    return decorated


class AuthHttpSession(Session):

    def __init__(self, client):
        super().__init__()
        client.authenticate(self)
        self.headers.update({'Content-Type': 'application/json'})
        self.hooks.update({'response': status_hook})

    def update_token(self, token):
        self.headers.update({'Authorization': "Bearer " + token})

    @retry_on_status(retries=3, statuses=(HTTP.SERVER_ERROR, HTTP.CONNECTION_RESET_BY_PEER, HTTP.TOO_MANY_REQUESTS,
                                          HTTP.SERVICE_UNAVAILABLE, HTTP.GATEWAY_TIMEOUT, HTTP.BAD_GATEWAY))
    def request(self, *args, **kwargs):
        return super().request(*args, **kwargs)
