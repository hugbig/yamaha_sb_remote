import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant.const import CONF_DEVICES, CONF_NAME, CONF_DEVICE_ID
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.entity import Entity

# LOGGING
_LOGGER = logging.getLogger(__name__)

# Supported domains
SUPPORTED_DOMAINS = ['media_player', 'switch', 'number', 'select']

# VERSION
#VERSION = '0.1.0'

# DOMAIN
DOMAIN = "yamaha_sr_c20a"

SCAN_INTERVAL = timedelta(seconds=15)

# DEFAULTS
DEFAULT_NAME = 'Yamaha SR-C20A'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES):
            vol.All(cv.ensure_list, [
                vol.Schema({
                    vol.Required("mac_adress", default='XX:XX:XX:XX'): cv.string,
                    vol.Required(CONF_DEVICE_ID): cv.string,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                    vol.Optional("polling_auto", default=False): cv.boolean,
                }),
            ]),
        })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Initialize the Soundbar device."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = []

    _LOGGER.info("Initializing Soundbar  devices")

    soundbar_list = []

    configured_devices = config[DOMAIN].get(CONF_DEVICES)
    for device in configured_devices:
        soundbar = SoundbarDevice(
            device.get("mac_adress"),
            device.get(CONF_DEVICE_ID),
            device.get(CONF_NAME),
            device.get("polling_auto"),
        )

        _LOGGER.debug("soundbar device %s configured", device.get(CONF_NAME))
        soundbar_list.append(soundbar)

    hass.data[DOMAIN] = soundbar_list

    if not soundbar_list:
        _LOGGER.info("No soundbar devices configured")
        return False

    _LOGGER.debug("Configured %s soundbars", len(soundbar_list))

    for domain in SUPPORTED_DOMAINS:
        hass.async_create_task(
            discovery.async_load_platform(hass, domain, DOMAIN, {}, config))
    return True

class SoundbarDevice(Entity):
    """Representation of a soundbar device."""

    def __init__(self, macAdress, device_id, name, polling_auto):
        """Initialize the Soundbar device."""
        self._name = name
        self._device_id = device_id
        self._macAdress = macAdress
        self._polling_auto = polling_auto

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
        return self._device_id

    @property
    def macAdress(self):
        return self._macAdress

    @property
    def pollingAuto(self):
        return self._polling_auto