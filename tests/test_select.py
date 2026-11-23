"""LED select."""

from tests.conftest import refresh, setup_integration



async def test_initial_read(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["led"]
    await refresh(hass, entity_id)
    assert hass.states.get(entity_id).state == "Bright"


async def test_select_off(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["led"]
    await refresh(hass, entity_id)

    await hass.services.async_call(
        "select", "select_option", {"entity_id": entity_id, "option": "Off"}, blocking=True
    )

    assert fake_bar.state.led == 2
    assert hass.states.get(entity_id).state == "Off"


async def test_no_refresh_without_polling(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["led"]
    await refresh(hass, entity_id)
    fake_bar.state.led = 1

    await refresh(hass, entity_id)

    assert hass.states.get(entity_id).state == "Bright"
