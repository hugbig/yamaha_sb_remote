"""Config flow."""

from homeassistant.data_entry_flow import FlowResultType

from custom_components.yamaha_sb_remote import DOMAIN
from tests.conftest import MAC

USER_INPUT = {"mac_adress": MAC, "name": "Yamaha SR-C20A", "polling_auto": False}


async def test_user_flow_creates_entry(hass):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Yamaha SR-C20A"
    assert result["data"] == USER_INPUT
