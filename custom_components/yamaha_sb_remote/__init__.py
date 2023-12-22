"""Fichier init."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.const import CONF_DEVICE_ID, CONF_DEVICES, CONF_NAME
from homeassistant.helpers import config_validation as cv

# LOGGING
_LOGGER = logging.getLogger(__name__)

# Supported domains
SUPPORTED_DOMAINS = ["media_player", "switch", "number", "select"]

# VERSION
# VERSION = '0.1.0'

# DOMAIN
DOMAIN = "yamaha_sb_remote"

SCAN_INTERVAL = timedelta(seconds=15)

# DEFAULTS
DEFAULT_NAME = "Yamaha SR-C20A"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICES): vol.All(
                    cv.ensure_list,
                    [
                        vol.Schema(
                            {
                                vol.Required(
                                    "mac_adress", default="XX:XX:XX:XX"
                                ): cv.string,
                                vol.Required(CONF_DEVICE_ID): cv.string,
                                vol.Optional(
                                    CONF_NAME, default=DEFAULT_NAME
                                ): cv.string,
                                vol.Optional("polling_auto", default=False): cv.boolean,
                            }
                        ),
                    ],
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass, config):
    """Initialize the Soundbar device."""
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(config, SUPPORTED_DOMAINS)
    return True
