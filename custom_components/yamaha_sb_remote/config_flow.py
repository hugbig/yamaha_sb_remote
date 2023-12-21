"""Config Flow."""

from custom_components.yamaha_sb_remote import _LOGGER, DOMAIN as SOUNDBAR_DOMAIN
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_DEVICE_ID, CONF_DEVICES, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

# DEFAULTS
DEFAULT_NAME = "Yamaha SR-C20A"


class ConfigFlow(ConfigFlow, domain=SOUNDBAR_DOMAIN):
    """Config flow implementation."""

    # La version de notre configFlow. Va permettre de migrer les entités
    # vers une version plus récente en cas de changement
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """User Step."""
        user_form = vol.Schema(
            {
                vol.Required("mac_adress", default="XX:XX:XX:XX"): cv.string,
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional("polling_auto", default=False): cv.boolean,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=user_form)

        # 2ème appel : il y a des user_input -> on stocke le résultat
        # TODO: utiliser les user_input
        _LOGGER.debug(
            "config_flow step user (2). On a reçu les valeurs: %s", user_input
        )
