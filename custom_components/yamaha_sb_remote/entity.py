"""Base class for the soundbar entities."""

from homeassistant.const import CONF_NAME
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_MANUFACTURER, DOMAIN
from .coordinator import YamahaSoundbarCoordinator


class YamahaEntity(CoordinatorEntity[YamahaSoundbarCoordinator]):
    """An entity of the soundbar device, fed by the coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: YamahaSoundbarCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_NAME],
            manufacturer=DEVICE_MANUFACTURER,
            model=DOMAIN,
        )

    async def _send(self, *commands: list) -> None:
        await self.coordinator.async_send_commands(list(commands))
