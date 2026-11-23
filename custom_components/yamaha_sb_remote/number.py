"""Subwoofer level."""

from homeassistant.components.number import NumberEntity, NumberMode

from homeassistant.exceptions import HomeAssistantError

from .entity import YamahaEntity
from .protocol import parse_status


class SoundbarSubwoofer(YamahaEntity, NumberEntity):
    """Subwoofer level, from -4 to 4."""

    _attr_name = "Subwoofer"
    _attr_native_min_value = -4
    _attr_native_max_value = 4
    _attr_native_step = 1
    _attr_mode = NumberMode.AUTO

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "subwoofer")

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.subwoofer

    async def async_set_native_value(self, value: float) -> None:
        target = int(value)
        if target == self.coordinator.data.subwoofer:
            return

        def steps_from(frame: bytes) -> list[list[str]]:
            # Relative steps, counted from the level read in this same connection.
            current = parse_status(frame).subwoofer
            if current is None:
                raise HomeAssistantError("The current subwoofer level is unknown")
            command = ["subUp"] if target > current else ["subDown"]
            return [command] * abs(target - current)

        await self.coordinator.async_send_commands(steps_from)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SoundbarSubwoofer(entry.runtime_data)])
