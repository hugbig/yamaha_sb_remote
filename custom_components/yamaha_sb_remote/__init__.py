"""Yamaha soundbar (Bluetooth) integration."""

from .const import DOMAIN, SUPPORTED_DOMAINS
from .coordinator import YamahaSoundbarCoordinator

__all__ = ["DOMAIN"]


async def async_setup_entry(hass, entry):
    """Set up the soundbar: read its state once, then the platforms."""
    coordinator = YamahaSoundbarCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_DOMAINS)
    return True


async def async_unload_entry(hass, entry):
    """Unload the platforms; the coordinator stops with the entry."""
    return await hass.config_entries.async_unload_platforms(entry, SUPPORTED_DOMAINS)
