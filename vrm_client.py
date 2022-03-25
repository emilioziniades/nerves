"""
Client to interact with VRM API. VRMClient handles login, access tokens, and requests.

"""
import json, logging
from os import environ
from pprint import pprint

import dotenv, requests

from config import TOKEN_NAME, TOKEN_URL, LOGIN_URL, TOKEN_REVOKE_URL, TOKEN_LIST_URL


class VRMClient:
    """
    VRMClient to handle connection to VRM API
    """

    def __init__(self):
        self.session = requests.Session()

        if not "VRM_TOKEN" in environ:
            logging.info("No access token found, generating one")
            self._generate_token(TOKEN_NAME)
        else:
            logging.info("Found access token")

        self.session.headers.update(
            {"X-Authorization": f"Token {environ.get('VRM_TOKEN')}"}
        )

        if not "VRM_USER_ID" in environ:
            logging.info("No user ID found, logging in")
            self._login()

        self.user_id = environ["VRM_USER_ID"]

    def _generate_token(self, token_name: str) -> None:
        # Fetches and saves access token and token ID to .env

        self._login()

        data = json.dumps({"name": token_name})
        req = self.session.post(TOKEN_URL.format(self.user_id), data=data)
        resp = json.loads(req.text)

        if req.status_code is requests.codes.ok and resp["success"]:
            logging.info("generate access token success")
        else:
            logging.critical(f"generate access token failed, exiting ... {req.text}")
            exit()

        with open(".env", "a") as f:
            f.write(f"VRM_TOKEN={resp.get('token')}\n")
            f.write(f"VRM_TOKEN_ID={resp.get('idAccessToken')}\n")
        dotenv.load_dotenv()

    def _login(self) -> None:
        # Logs into VRM API with username and password
        try:
            username, password = environ["VRM_USERNAME"], environ["VRM_PASSWORD"]
        except KeyError:
            logging.critical(
                "Please create a .env file in this directory and supply VRM_USERNAME and VRM_PASSWORD. Exiting..."
            )
            exit()

        data = json.dumps({"username": username, "password": password})
        req = self.session.post(LOGIN_URL, data=data)
        resp = json.loads(req.text)

        if req.status_code is requests.codes.ok:
            logging.info("login successful")
        else:
            logging.critical(f"login failed, exiting... {req.text}")
            exit()

        with open(".env", "a") as f:
            f.write(f"VRM_USER_ID={resp.get('idUser')}\n")
        dotenv.load_dotenv()

        self.session.headers.update({"X-Authorization": f"Bearer {resp.get('token')}"})

    def list_tokens(self) -> None:
        req = self.session.get(TOKEN_LIST_URL.format(self.user_id))

        if req.status_code is requests.codes.ok:
            logging.info("listing access tokens successful")
        else:
            logging.error(f"listing access tokens failed... {req.text}")

        pprint(req.json()["tokens"])

    def revoke_token(self, token_id: str) -> None:
        req = self.session.get(TOKEN_REVOKE_URL.format(self.user_id, token_id))
        if req.status_code is requests.codes.ok:
            logging.info("token revocation successful")
        else:
            logging.error(f"token revocation failed {req.text}")

    def get_installations(self):
        pass
