"""Config Flow."""

from custom_components.yamaha_sb_remote import DOMAIN as SOUNDBAR_DOMAIN
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_DEVICE_ID, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

# DEFAULTS
DEFAULT_NAME = "Yamaha SR-C20A"


class ConfigFlow(ConfigFlow, domain=SOUNDBAR_DOMAIN):
    """Config flow implementation."""

    VERSION = 1
    _user_inputs: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """User Step."""
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")
        user_form = vol.Schema(
            {
                vol.Required("mac_adress", default="XX:XX:XX:XX"): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Optional("polling_auto", default=False): cv.boolean,
            }
        )

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=user_form)

        self._user_inputs.update(user_input)

        return self.async_create_entry(
            title=self._user_inputs[CONF_NAME], data=self._user_inputs
        )
