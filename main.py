import logging
import pprint

import dotenv

import vrm_client
from config import BASE_URL


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    dotenv.load_dotenv()

    logging.info("starting...")

    vrm = vrm_client.VRMClient()
    vrm.list_tokens()

    # req = vrm.session.get(
    #     os.path.join(BASE_URL, "users", vrm.user_id, "installations"),
    # )
    # print(req.status_code)
    # pprint.pprint(req.json())


if __name__ == "__main__":
    main()
