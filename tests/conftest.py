"""Shared fixtures for the yamaha_sb_remote tests."""

from types import SimpleNamespace

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_component import async_update_entity
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.yamaha_sb_remote import ble_connect
from tests.fake_soundbar import FakeSoundbar

DOMAIN = "yamaha_sb_remote"
MAC = "AA:BB:CC:DD:EE:FF"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Let Home Assistant load the integration from custom_components."""
    yield


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A config entry with the keys the config flow creates."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Yamaha SR-C20A",
        data={"mac_adress": MAC, "name": "Yamaha SR-C20A", "polling_auto": False},
    )


@pytest.fixture
def fake_bar(monkeypatch) -> FakeSoundbar:
    """Replace the BLE stack with a fake soundbar."""
    bar = FakeSoundbar()

    def ble_device_from_address(hass, address, connectable=True):
        return SimpleNamespace(address=address) if bar.reachable else None

    async def establish_connection(client_class, device, name, *args, **kwargs):
        return await bar.connect()

    monkeypatch.setattr(ble_connect, "establish_connection", establish_connection)
    monkeypatch.setattr(
        ble_connect.bluetooth, "async_ble_device_from_address", ble_device_from_address
    )
    monkeypatch.setattr(ble_connect, "STATUS_TIMEOUT", 0.3)
    return bar


ENTITIES = {
    "media_player": ("media_player", "mediaplayer"),
    "clear_voice": ("switch", "clear_voice"),
    "bass_ext": ("switch", "bass_ext"),
    "subwoofer": ("number", "subwoofer"),
    "led": ("select", "led"),
}


async def setup_integration(hass, config_entry) -> dict[str, str]:
    """Set up the config entry; return the entity ids, looked up by unique id."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    return {
        key: registry.async_get_entity_id(platform, DOMAIN, f"{config_entry.entry_id}_{suffix}")
        for key, (platform, suffix) in ENTITIES.items()
    }


async def refresh(hass, entity_id: str) -> None:
    """Run the entity's update, as a polling cycle would."""
    await async_update_entity(hass, entity_id)
    await hass.async_block_till_done()
