import os, json, logging
from pprint import pprint

from dotenv import load_dotenv
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()
BASE_URL = "https://vrmapi.victronenergy.com/v2/"


class TokenManager:
    def __init__(self):
        try:
            username, password = os.environ["VRM_USERNAME"], os.environ["VRM_PASSWORD"]
        except KeyError:
            logging.critical(
                "Please create a .env file in this directory and supply VRM_USERNAME and VRM_PASSWORD. Exiting..."
            )
            exit()

        self.session = requests.Session()
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

        self.user_id = str(resp["idUser"])
        self.session.headers.update({"X-Authorization": f"Bearer {resp.get('token')}"})

    def generate_token(self, token_name: str) -> None:
        """
        Fetches and saves access token and token ID to .env
        """

        # generate access token and save to .env
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


def main() -> None:

    tm = TokenManager()
    tm.list_tokens()
    # tm.generate_token("Emilio Ziniades")
    # tm.list_tokens()


if __name__ == "__main__":
    main()
