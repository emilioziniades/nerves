import json
import os
import logging
from typing import Tuple, List
from pprint import pprint

from dotenv import load_dotenv
import requests

logging.basicConfig(level=logging.INFO)
load_dotenv()
BASE_URL = "https://vrmapi.victronenergy.com/v2/"


def login(ses: requests.Session) -> str:
    """
    Fetches data required for subsequent API calls. requests.Session object updated with bearer token header. Requires VRM_USERNAME and VRM_PASSWORD to be set in .env file
    """
    username, password = os.environ["VRM_USERNAME"], os.environ["VRM_PASSWORD"]

    # login and get user id
    req = ses.post(
        os.path.join(BASE_URL, "auth", "login"),
        data=json.dumps({"username": username, "password": password}),
    )
    resp = json.loads(req.text)

    if req.status_code is requests.codes.ok:
        logging.info("login successful")
    else:
        logging.critical(f"login failed, exiting... {req.text}")
        exit()

    ses.headers.update({"X-Authorization": f"Bearer {resp.get('token')}"})
    return str(resp["idUser"])


def generate_token(ses: requests.Session, user_id: str, token_name: str) -> None:
    """
    Fetches and saves access token and token ID to .env
    """

    # generate access token and save to .env
    req = ses.post(
        os.path.join(BASE_URL, "users", user_id, "accesstokens", "create"),
        data=json.dumps({"name": token_name}),
    )
    print(req.status_code, req.text)
    resp = json.loads(req.text)

    if req.status_code is requests.codes.ok and resp["success"]:
        logging.info("generate access token success")
    else:
        logging.critical(f"generate access token failed, exiting ... {req.text}")
        exit()

    with open(".env", "a") as f:
        f.write(f"VRM_TOKEN={resp.get('token')}\n")
        f.write(f"VRM_TOKEN_ID={resp.get('idAccessToken')}\n")


def list_tokens(ses: requests.Session, user_id: str) -> None:
    """
    Lists all active access tokens
    """

    req = ses.get(
        os.path.join(BASE_URL, "users", user_id, "accesstokens", "list"),
    )

    if req.status_code is requests.codes.ok:
        logging.info("fetching access tokens successful")
    else:
        logging.error(f"fetching access tokens failed... {req.text}")

    pprint(req.json()["tokens"])


def revoke_token(ses: requests.Session, user_id: str, token_id: str) -> None:
    """Revokes stipulated access token"""

    req = ses.get(
        os.path.join(BASE_URL, "users", user_id, "accesstokens", token_id, "revoke"),
    )
    print(req.status_code, req.text)

    if req.status_code is requests.codes.ok:
        logging.info("token revocation successful")
    else:
        logging.error(f"token revocation failed {req.text}")


def main() -> None:

    ses = requests.Session()
    user_id = login(ses)
    list_tokens(ses, user_id)
    generate_token(ses, user_id, "Emilio Ziniades")
    list_tokens(ses, user_id)


if __name__ == "__main__":
    main()
