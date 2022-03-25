import logging, os
from pprint import pprint

import dotenv

import vrm_client
from config import BASE_URL


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.info("starting...")
    dotenv.load_dotenv()

    vrm = vrm_client.VRMClient()

    req = vrm.session.get(
        os.path.join(BASE_URL, "users", vrm.user_id, "installations"),
    )

    req = vrm.session.get(
        os.path.join(BASE_URL, "users", vrm.user_id, "system-overview"),
    )
    data = req.json()
    pprint(data)


if __name__ == "__main__":
    main()
