"""Setting up a config entry."""

from datetime import timedelta

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.yamaha_sb_remote import DOMAIN
from tests.conftest import MAC, setup_integration

REQUEST = bytes.fromhex("ccaa020305f6")

SUFFIXES = {"mediaplayer", "clear_voice", "bass_ext", "subwoofer", "led"}


async def test_setup_creates_five_entities(hass, config_entry, fake_bar):
    await setup_integration(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    unique_ids = {
        entry.unique_id
        for entry in er.async_entries_for_config_entry(er.async_get(hass), config_entry.entry_id)
    }
    assert unique_ids == {f"{config_entry.entry_id}_{suffix}" for suffix in SUFFIXES}
    # One connection reads the state for all five entities.
    assert fake_bar.written == [REQUEST]


async def test_setup_when_bar_unreachable(hass, config_entry, fake_bar):
    fake_bar.reachable = False
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert er.async_entries_for_config_entry(er.async_get(hass), config_entry.entry_id) == []

    fake_bar.reachable = True
    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    assert len(er.async_entries_for_config_entry(er.async_get(hass), config_entry.entry_id)) == 5


async def test_unload_and_reload(hass, fake_bar):
    # Polling on, so a refresh is scheduled and must not survive the unload.
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Yamaha SR-C20A",
        data={"mac_adress": MAC, "name": "Yamaha SR-C20A", "polling_auto": True},
    )
    await setup_integration(hass, config_entry)

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
    written = len(fake_bar.written)

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=120))
    await hass.async_block_till_done()
    assert len(fake_bar.written) == written

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
