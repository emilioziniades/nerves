"""
Client to interact with VRM API. VRMClient handles login, access tokens, and requests.

"""
import json, logging
from os import environ
from pprint import pprint
from typing import Dict, Tuple, List
from datetime import datetime, timedelta

import dotenv, requests

from config import (
    TOKEN_NAME,
    TOKEN_ENDPOINT,
    AUTH_ENDPOINT,
    TOKEN_REVOKE_ENDPOINT,
    TOKEN_LIST_ENDPOINT,
    INSTALLATIONS_ENDPOINT,
    STATS_ENDPOINT,
    WIDGET_ENDPOINT,
)


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
        req = self.session.post(TOKEN_ENDPOINT.format(self.user_id), data=data)
        check_ok(req, "generate access token", should_exit=True)

        resp = req.json()
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
        req = self.session.post(AUTH_ENDPOINT, data=data)
        check_ok(req, "login", should_exit=True)
        resp = req.json()

        with open(".env", "a") as f:
            f.write(f"VRM_USER_ID={resp.get('idUser')}\n")
        dotenv.load_dotenv()

        self.session.headers.update({"X-Authorization": f"Bearer {resp.get('token')}"})

    def list_tokens(self) -> Dict:
        url = TOKEN_LIST_ENDPOINT.format(user_id=self.user_id)
        req = self.session.get(url)
        check_ok(req, "listing access tokens")
        return req.json()["tokens"]

    def revoke_token(self, token_id: str) -> None:
        url = TOKEN_REVOKE_ENDPOINT.format(user_id=self.user_id, token_id=token_id)
        req = self.session.get(url)
        check_ok(req, "token revocation")

    def lookup_site(self, site_name: str) -> str:
        sites = self.get_installations()
        site_names = [i for i in sites.keys()]
        try:
            site_id = sites[site_name]
            return site_id
        except KeyError:
            logging.error(f"site '{site_name}' not found. Sites include: {site_names} ")
            return ""

    def get_installations(self) -> Dict[str, str]:
        url = INSTALLATIONS_ENDPOINT.format(user_id=self.user_id)
        req = self.session.get(url)
        check_ok(req, "fetch installations")
        resp = req.json()
        return {i["name"]: str(i["idSite"]) for i in resp["records"]}

    def get_kwh_stats(self, diff: int, site_id: str) -> Dict:

        start, end = timestamps_until_now(diff, round=False)

        payload = {
            "type": "kwh",
            "start": start,
            "end": end,
            "interval": "hours",
        }

        req = self.session.get(STATS_ENDPOINT.format(site_id=site_id), params=payload)
        check_ok(req, "fetch kwh readings")
        resp = req.json()

        return resp

    def get_custom_stats(
        self, diff: int, site_id: str, readings: List[str], round: bool = False
    ) -> Dict:
        start, end = timestamps_until_now(diff, round=round)

        payload = {
            "type": "custom",
            "start": start,
            "end": end,
            "interval": "hours",
            "attributeCodes[]": readings,
        }

        req = self.session.get(STATS_ENDPOINT.format(site_id=site_id), params=payload)
        check_ok(req, "fetch custom readings")
        resp = req.json()

        return resp


def check_ok(r: requests.Response, action: str, should_exit: bool = False) -> None:
    # verifies status code of http request, and logs result
    response = r.json()
    if r.status_code is requests.codes.ok and response["success"]:
        logging.info(f"{action} successful")
    else:
        if should_exit:
            logging.critical(f"{action} failed, exiting ... {response}")
            exit(1)
        else:
            logging.error(f"{action} failed ... {response}")


def round_hours(t: datetime) -> datetime:
    # rounds down to the nearest hour
    return t.replace(microsecond=0, second=0, minute=0)


def timestamps_until_now(diff: int, round: bool = False) -> Tuple[str, str]:
    # returns timestamps (start, end) where end is now, and start is diff hours in the past
    now = datetime.now()
    prev = now - timedelta(hours=diff)
    if round:
        now = round_hours(now)
        prev = round_hours(prev)
    start = int(prev.timestamp())
    end = int(now.timestamp())

    return str(start), str(end)
