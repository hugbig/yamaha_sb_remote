"""Fichier init."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.const import CONF_DEVICES, CONF_NAME
from homeassistant.helpers import config_validation as cv

# LOGGING
_LOGGER = logging.getLogger(__name__)

# Supported domains
SUPPORTED_DOMAINS = ["media_player", "switch", "number", "select"]

# VERSION
# VERSION = '0.1.0'

# DOMAIN
DOMAIN = "yamaha_sb_remote"

DEVICE_MANUFACTURER = "YAMAHA"

SCAN_INTERVAL = timedelta(seconds=15)

# DEFAULTS
DEFAULT_NAME = "Yamaha SR-C20A"


async def async_setup_entry(hass, config):
    """Initialize the Soundbar device."""
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(config, SUPPORTED_DOMAINS)
    return True
