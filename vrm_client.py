import os, json, logging
from pprint import pprint

import dotenv, requests

from config import BASE_URL


class VRMClient:
    def __init__(self):
        self.session = requests.Session()
        if not os.environ.get("VRM_TOKEN"):
            logging.info("No access token found, generating one")
            self.generate_token("Emilio Ziniades")

        dotenv.load_dotenv()

        if not os.environ.get("VRM_USER_ID"):
            logging.info("No user ID found, logging in")
            self.login()

        dotenv.load_dotenv()

        self.user_id = os.environ["VRM_USER_ID"]
        self.session.headers.update(
            {"X-Authorization": f"Token {os.environ.get('VRM_TOKEN')}"}
        )

    def generate_token(self, token_name: str) -> None:
        """
        Fetches and saves access token and token ID to .env
        """

        self.login()

        req = self.session.post(
            os.path.join(BASE_URL, "users", self.user_id, "accesstokens", "create"),
            data=json.dumps({"name": token_name}),
        )
        resp = json.loads(req.text)

        if req.status_code is requests.codes.ok and resp["success"]:
            logging.info("generate access token success")
        else:
            logging.critical(f"generate access token failed, exiting ... {req.text}")
            exit()

        with open(".env", "a") as f:
            f.write(f"VRM_TOKEN={resp.get('token')}\n")
            f.write(f"VRM_TOKEN_ID={resp.get('idAccessToken')}\n")

    def login(self) -> None:
        try:
            username, password = os.environ["VRM_USERNAME"], os.environ["VRM_PASSWORD"]
        except KeyError:
            logging.critical(
                "Please create a .env file in this directory and supply VRM_USERNAME and VRM_PASSWORD. Exiting..."
            )
            exit()

        req = self.session.post(
            os.path.join(BASE_URL, "auth", "login"),
            data=json.dumps({"username": username, "password": password}),
        )
        resp = json.loads(req.text)

        if req.status_code is requests.codes.ok:
            logging.info("login successful")
        else:
            logging.critical(f"login failed, exiting... {req.text}")
            exit()

        with open(".env", "a") as f:
            f.write(f"VRM_USER_ID={resp.get('idUser')}\n")

        self.session.headers.update({"X-Authorization": f"Bearer {resp.get('token')}"})

    def list_tokens(self) -> None:
        """
        Lists all active access tokens
        """

        req = self.session.get(
            os.path.join(BASE_URL, "users", self.user_id, "accesstokens", "list"),
        )

        if req.status_code is requests.codes.ok:
            logging.info("listing access tokens successful")
        else:
            logging.error(f"listing access tokens failed... {req.text}")

        pprint(req.json()["tokens"])

    def revoke_token(self, token_id: str) -> None:
        """Revokes stipulated access token"""

        req = self.session.get(
            os.path.join(
                BASE_URL, "users", self.user_id, "accesstokens", token_id, "revoke"
            ),
        )
        if req.status_code is requests.codes.ok:
            logging.info("token revocation successful")
        else:
            logging.error(f"token revocation failed {req.text}")
