"""Subwoofer number."""

import pytest

from tests.conftest import refresh, setup_integration

SUB_UP = bytes.fromhex("ccaa0340784cf9")


async def set_value(hass, entity_id, value):
    await hass.services.async_call(
        "number", "set_value", {"entity_id": entity_id, "value": value}, blocking=True
    )


async def test_initial_read(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    await refresh(hass, entity_id)
    assert float(hass.states.get(entity_id).state) == 0


async def test_set_value_steps_up(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    await refresh(hass, entity_id)

    await set_value(hass, entity_id, 2)

    assert fake_bar.written.count(SUB_UP) == 2
    assert fake_bar.state.sub == 24
    assert float(hass.states.get(entity_id).state) == 2


async def test_set_same_value_sends_nothing(hass, config_entry, fake_bar):
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    await refresh(hass, entity_id)
    written = len(fake_bar.written)

    await set_value(hass, entity_id, 0)

    assert len(fake_bar.written) == written


@pytest.mark.xfail(
    strict=True, raises=TypeError, reason="native_value is None before the first read, fixed in lot 3")
async def test_number_set_before_first_read(hass, config_entry, fake_bar):
    fake_bar.reachable = False
    entity_id = (await setup_integration(hass, config_entry))["subwoofer"]
    await refresh(hass, entity_id)

    await set_value(hass, entity_id, 1)
