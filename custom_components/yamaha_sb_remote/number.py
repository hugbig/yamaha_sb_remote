from .ble_connect import BleData

from custom_components.yamaha_sb_remote import _LOGGER, DOMAIN as SOUNDBAR_DOMAIN
from homeassistant.components.number import (
    NumberEntity,
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up platform."""
    """Initialize the Soundbar device."""
    devices = []
    soundbar_list = hass.data[SOUNDBAR_DOMAIN]

    for device in soundbar_list:
        _LOGGER.debug("Configured a new SoundbarNumber %s", device.name)
        devices.append(SoundbarNumber(hass, device))

    async_add_entities(devices)


class SoundbarNumber(NumberEntity):
    def __init__(self, hass, DeviceEntity):
        self._state = None
        self._sub = None
        self._type = "subwoofer"
        self.hass = hass
        self._macAdress = DeviceEntity.macAdress
        self._device_id = DeviceEntity.device_id
        self._name = DeviceEntity.name + "_subwoofer"
        self._pollingAuto = DeviceEntity.pollingAuto
        self._status = "unint"
        self._attr_native_max_value = 4
        self._attr_native_min_value = -4
        self._attr_native_step = 1
        self._attr_native_value = None
        self._attr_mode = "auto"

    # Run when added to HASS TO LOAD SOURCES
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._device_id + "_" + self._type

    async def async_update(self):
        """Update the Number State."""
        if self._status == "unint" or self._pollingAuto is True:
            ble_connect = BleData(self, self.hass, self._macAdress)
            await ble_connect.callDevice()
            if self._status == "init":
                if self._sub is not None:
                    self._state = self._sub
                    self._attr_native_value = self._sub

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        ble_connect = BleData(self, self.hass, self._macAdress)
        stepNumber = int(value) - self._attr_native_value
        if stepNumber >= 0:
            for i in range(stepNumber):
                await ble_connect.callDevice(["subUp"])
        else:
            stepNumber = stepNumber * -1
            for i in range(stepNumber):
                await ble_connect.callDevice(["subDown"])
        self._attr_native_value = value
        self._state = value
