import logging
from pprint import pprint
from datetime import datetime

import dotenv

import vrm_client


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.info("starting...")
    dotenv.load_dotenv()

    vrm = vrm_client.VRMClient()

    data = vrm.get_readings(diff=24, site="Longmarket")
    pprint(data)
    pc = data["records"]["kwh"]
    for i in pc:
        curr = i[0] / 1000
        # print(i[0])
        print(i[0], datetime.fromtimestamp(curr))


if __name__ == "__main__":
    main()
