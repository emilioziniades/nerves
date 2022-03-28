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
    lm_id = vrm.lookup_site("Longmarket")
    readings = ["dpE", "dYU"]
    data = vrm.get_custom_stats(diff=24, site_id=lm_id, readings=readings, round=True)
    pprint(data)

    for k, v in data["records"].items():
        print(k)
        for i in v:
            print(i[0], datetime.fromtimestamp(i[0] / 1000), i[1])


if __name__ == "__main__":
    main()
