from typing import Dict
import json
import os
import logging
import glob

from django.conf import settings

logger = logging.getLogger("alexandria")

with open(os.path.join("alexandria", "default.json"), "r") as base_json:
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
