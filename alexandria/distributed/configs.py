from typing import Dict
import json
import os
import logging
import glob

from django.conf import settings

logger = logging.getLogger("alexandria")


def init_site_data():
    with open(
        os.path.join("alexandria", "distributed", "default.json"), "r"
    ) as base_json:
        sites: Dict = json.load(base_json)
        logger.info("Loaded default site information!")

    if os.path.exists(os.path.join(settings.BASE_DIR, "configs")):
        logger.info("Cloud config directory found, merging configs into site object.")
        config_files = glob.glob(os.path.join(settings.BASE_DIR, "configs", "*.json"))
        logger.info(f"Found {len(config_files)} cloud configs.")

        for conf in config_files:
            with open(conf, "r") as conf_file:
                data = json.load(conf_file)
                domain = list(data.keys()[0])
                logger.debug(f"Loading {domain}...")
                sites[domain] = data[domain]
    return sites


def load_site_config(domain: str) -> Dict:
    if domain in settings.DEFAULT_HOSTS or domain == settings.DEFAULT_HOST_KEY:
        return settings.SITE_DATA[settings.DEFAULT_HOST_KEY]

    if domain in settings.SITE_DATA:
        config = settings.SITE_DATA[domain]
        for key in settings.SITE_DATA[settings.DEFAULT_HOST_KEY].keys():
            # make sure that any missing fields are populated with the defaults
            if not config.get(key):
                config[key] = settings.SITE_DATA[settings.DEFAULT_HOST_KEY][key]
        return config

    return {}
