"""Support for Satel Integra zone states- represented as binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .entity import SatelIntegraEntity
from .const import (
    CONF_OUTPUTS,
    CONF_ZONE_NAME,
    CONF_ZONE_TYPE,
    CONF_ZONES,
    CONF_ZONES_ALARM,
    CONF_ZONES_MEM_ALARM,
    CONF_ZONES_TAMPER,
    CONF_ZONES_MEM_TAMPER,
    CONF_ZONES_BYPASS,
    CONF_ZONES_MASKED,
    CONF_ZONES_MEM_MASKED,
    DATA_SATEL,
    SIGNAL_OUTPUTS_UPDATED,
    SIGNAL_VIOLATED_UPDATED,
    SIGNAL_ALARM_UPDATED,
    SIGNAL_MEM_ALARM_UPDATED,
    SIGNAL_TAMPER_UPDATED,
    SIGNAL_MEM_TAMPER_UPDATED,
    SIGNAL_BYPASS_UPDATED,
    SIGNAL_MASKED_UPDATED,
    SIGNAL_MEM_MASKED_UPDATED
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Satel Integra binary sensor devices."""
    if not discovery_info:
        return

    configured_zones = discovery_info[CONF_ZONES]
    controller = hass.data[DATA_SATEL]

    devices = []

    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME]
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES, 
            SIGNAL_VIOLATED_UPDATED
        )
        devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (alarm)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_ALARM, 
            SIGNAL_ALARM_UPDATED
        )
        devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (mem alarm)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_MEM_ALARM, 
            SIGNAL_MEM_ALARM_UPDATED
        )
        devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (tamper)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_TAMPER, 
            SIGNAL_TAMPER_UPDATED
        )
        devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (mem tamper)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_MEM_TAMPER, 
            SIGNAL_MEM_TAMPER_UPDATED
        )
        devices.append(device)
    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (bypass)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_BYPASS, 
            SIGNAL_BYPASS_UPDATED
        )
        devices.append(device)
    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (masked)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_MASKED, 
            SIGNAL_MASKED_UPDATED
        )
        devices.append(device)
    for zone_num, device_config_data in configured_zones.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME] + ' (mem masked)'
        device = SatelIntegraBinarySensor(
            controller, 
            zone_num, 
            zone_name, 
            zone_type, 
            CONF_ZONES_MEM_MASKED, 
            SIGNAL_MEM_MASKED_UPDATED
        )
        devices.append(device)

    configured_outputs = discovery_info[CONF_OUTPUTS]

    for zone_num, device_config_data in configured_outputs.items():
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_ZONE_NAME]
        device = SatelIntegraBinarySensor(
            controller, zone_num, zone_name, zone_type, "output", SIGNAL_OUTPUTS_UPDATED
        )
        devices.append(device)

    async_add_entities(devices)


class SatelIntegraBinarySensor(SatelIntegraEntity, BinarySensorEntity):
    """Representation of an Satel Integra binary sensor."""

    _attr_should_poll = False

    def __init__(
        self, controller, device_number, device_name, zone_type, device_type, react_to_signal
    ):
        """Initialize the binary_sensor."""
        super().__init__(controller, device_number, device_name, device_type)
        self._zone_type = zone_type
        self._state = 0
        self._react_to_signal = react_to_signal

    async def async_added_to_hass(self) -> None:
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            if self._device_number in self._satel.violated_outputs:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_VIOLATED_UPDATED:
            if self._device_number in self._satel.violated_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_ALARM_UPDATED:
            if self._device_number in self._satel.alarm_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_MEM_ALARM_UPDATED:
            if self._device_number in self._satel.mem_alarm_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_TAMPER_UPDATED:
            if self._device_number in self._satel.tamper_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_MEM_TAMPER_UPDATED:
            if self._device_number in self._satel.mem_tamper_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            if self._device_number in self._satel.bypass_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_MASKED_UPDATED:
            if self._device_number in self._satel.masked_zones:
                self._state = 1
            else:
                self._state = 0
        elif self._react_to_signal == SIGNAL_MEM_MASKED_UPDATED:
            if self._device_number in self._satel.mem_masked_zones:
                self._state = 1
            else:
                self._state = 0
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._react_to_signal, self._devices_updated
            )
        )

    @property
    def icon(self):
        """Icon for device by its type."""
        if self._zone_type is BinarySensorDeviceClass.SMOKE:
            return "mdi:fire"

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state == 1

    @property
    def device_class(self):
        """Return the class of this sensor, from DEVICE_CLASSES."""
        return self._zone_type

    @callback
    def _devices_updated(self, zones):
        """Update the zone's state, if needed."""
        if self._device_number in zones and self._state != zones[self._device_number]:
            self._state = zones[self._device_number]
            self.async_write_ha_state()
