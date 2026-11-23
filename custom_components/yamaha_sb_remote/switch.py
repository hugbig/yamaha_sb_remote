"""Clear Voice and Bass Extension switches."""

from homeassistant.components.switch import SwitchEntity

from .entity import YamahaEntity

# key (keeps the unique id), name, state field, on command, off command
SWITCHES = [
    ("clear_voice", "Clear Voice", "clear_voice", "clearVoiceOn", "clearVoiceOff"),
    ("bass_ext", "Bass Extension", "bass_ext", "bassOn", "bassOff"),
]


class SoundbarSwitch(YamahaEntity, SwitchEntity):
    """A soundbar feature that can be turned on or off."""

    def __init__(self, coordinator, key, name, field, on_command, off_command) -> None:
        super().__init__(coordinator, key)
        self._attr_name = name
        self._field = field
        self._on_command = on_command
        self._off_command = off_command

    @property
    def is_on(self) -> bool:
        return getattr(self.coordinator.data, self._field)

    async def async_turn_on(self, **kwargs) -> None:
        await self._send([self._on_command])

    async def async_turn_off(self, **kwargs) -> None:
        await self._send([self._off_command])


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(SoundbarSwitch(entry.runtime_data, *switch) for switch in SWITCHES)
