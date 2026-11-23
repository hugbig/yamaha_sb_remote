"""Front LED brightness."""

from homeassistant.components.select import SelectEntity

from .entity import YamahaEntity
from .protocol import LEDS

LED_COMMANDS = {"Bright": "ledBright", "Dim": "ledDim", "Off": "ledOff"}
assert set(LED_COMMANDS) == set(LEDS.values())


class SoundbarLed(YamahaEntity, SelectEntity):
    """Front LED brightness."""

    _attr_name = "LED"
    _attr_options = list(LEDS.values())

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "led")

    @property
    def current_option(self) -> str | None:
        return self.coordinator.data.led

    async def async_select_option(self, option: str) -> None:
        await self._send([LED_COMMANDS[option]])


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SoundbarLed(entry.runtime_data)])
