"""The coordinator: polling, retries and availability."""

from datetime import timedelta

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.yamaha_sb_remote.coordinator import RETRY_INTERVAL
from tests.conftest import DOMAIN, MAC, setup_integration


async def advance(hass, seconds):
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=seconds))
    await hass.async_block_till_done(wait_background_tasks=True)


async def test_polling_interval(hass, fake_bar):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Yamaha SR-C20A",
        data={"mac_adress": MAC, "name": "Yamaha SR-C20A", "polling_auto": True},
    )
    await setup_integration(hass, entry)
    before = len(fake_bar.written)

    await advance(hass, 31)

    assert len(fake_bar.written) == before + 1


async def test_no_polling_when_disabled(hass, config_entry, fake_bar):
    await setup_integration(hass, config_entry)
    before = len(fake_bar.written)

    await advance(hass, 120)

    assert len(fake_bar.written) == before


async def test_transient_failure_is_retried(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    coordinator = config_entry.runtime_data
    fake_bar.fail_next = 1

    await coordinator.async_refresh()

    assert coordinator.last_update_success is True
    assert hass.states.get(ids["media_player"]).state != STATE_UNAVAILABLE


async def test_two_failures_make_entities_unavailable_then_recover(hass, config_entry, fake_bar):
    ids = await setup_integration(hass, config_entry)
    coordinator = config_entry.runtime_data
    fake_bar.answer_status = False

    await coordinator.async_refresh()
    await hass.async_block_till_done(wait_background_tasks=True)

    assert hass.states.get(ids["media_player"]).state == STATE_UNAVAILABLE
    assert coordinator.update_interval == RETRY_INTERVAL

    fake_bar.answer_status = True
    await advance(hass, 61)

    assert hass.states.get(ids["media_player"]).state != STATE_UNAVAILABLE
    assert coordinator.update_interval is None
