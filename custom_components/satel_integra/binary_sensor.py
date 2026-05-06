"""Support for Satel Integra zone states- represented as binary sensors."""
from __future__ import annotations

import logging
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

from .entity import SatelIntegraEntity
from .const import (
    CONF_OUTPUTS,
    CONF_NAME,
    CONF_ZONE_TYPE,
    CONF_ZONE_MASK,
    CONF_ZONE_TAMPER,
    CONF_ZONES,
    CONF_ZONES_ALARM,
    CONF_ZONES_MEM_ALARM,
    CONF_ZONES_TAMPER,
    CONF_ZONES_MEM_TAMPER,
    CONF_ZONES_BYPASS,
    CONF_ZONES_MASKED,
    CONF_ZONES_MEM_MASKED,
    CONF_TROUBLE,
    CONF_TROUBLE2,
    
    CONF_KEYPAD,
    CONF_EXPANDER_BATTERY,
    CONF_EXPANDER,
    DATA_SATEL,
    SIGNAL_OUTPUTS_UPDATED,
    SIGNAL_VIOLATED_UPDATED,
    SIGNAL_ALARM_UPDATED,
    SIGNAL_MEM_ALARM_UPDATED,
    SIGNAL_TAMPER_UPDATED,
    SIGNAL_MEM_TAMPER_UPDATED,
    SIGNAL_BYPASS_UPDATED,
    SIGNAL_MASKED_UPDATED,
    SIGNAL_MEM_MASKED_UPDATED,
    SIGNAL_TROUBLE_UPDATED,
    SIGNAL_TROUBLE2_UPDATED,
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
        zone_name = device_config_data[CONF_NAME]
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
        zone_name = device_config_data[CONF_NAME] + ' (alarm)'
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
        zone_name = device_config_data[CONF_NAME] + ' (mem alarm)'
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
        try:
            zone_tamper = device_config_data[CONF_ZONE_TAMPER]
        except KeyError:
            zone_tamper = "no"
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_NAME] + ' (tamper)'
        if zone_tamper == "yes":
            device = SatelIntegraBinarySensor(controller, zone_num, zone_name, "tamper", CONF_ZONES_TAMPER, SIGNAL_TAMPER_UPDATED)
            devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        try:
            zone_tamper = device_config_data[CONF_ZONE_TAMPER]
        except KeyError:
            zone_tamper = "no"
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_NAME] + ' (mem tamper)'
        if zone_tamper == "yes":
             device = SatelIntegraBinarySensor(controller, zone_num, zone_name, "tamper", CONF_ZONES_MEM_TAMPER, SIGNAL_MEM_TAMPER_UPDATED)
             devices.append(device)
        
    
    for zone_num, device_config_data in configured_zones.items():
        try:
            zone_mask = device_config_data[CONF_ZONE_MASK]
        except KeyError:
            zone_mask = "no"
    
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_NAME] + ' (masked)'
        if zone_mask == "yes":
            device = SatelIntegraBinarySensor(controller, zone_num, zone_name, "problem", CONF_ZONES_MASKED, SIGNAL_MASKED_UPDATED)
            devices.append(device)

    for zone_num, device_config_data in configured_zones.items():
        try:
            zone_mask = device_config_data[CONF_ZONE_MASK]
        except KeyError:
            zone_mask = "no"
        zone_type = device_config_data[CONF_ZONE_TYPE]
        zone_name = device_config_data[CONF_NAME] + ' (mem masked)'
        if zone_mask == "yes":
            device = SatelIntegraBinarySensor(controller, zone_num, zone_name, "problem", CONF_ZONES_MEM_MASKED, SIGNAL_MEM_MASKED_UPDATED)
            devices.append(device)

    configured_outputs = discovery_info[CONF_OUTPUTS]

    for output_num, device_config_data in configured_outputs.items():
        output_type = device_config_data[CONF_ZONE_TYPE]
        output_name = device_config_data[CONF_NAME]
        device = SatelIntegraBinarySensor(
            controller, output_num, output_name, output_type, "output", SIGNAL_OUTPUTS_UPDATED
        )
        devices.append(device)
    
    configured_expanders = discovery_info[CONF_EXPANDER]
       
    for zone_num, device_config_data in configured_expanders.items():
        zone_name = device_config_data[CONF_NAME]
        battery = device_config_data[CONF_EXPANDER_BATTERY]
        
        device = SatelIntegraBinarySensor(controller, zone_num+1, zone_name + " (no comm)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)
        device = SatelIntegraBinarySensor(controller, zone_num + 1 + 64, zone_name + " (changed)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)
        device = SatelIntegraBinarySensor(controller, zone_num +1 + 64 + 64 + 8 + 8 + 8, zone_name + " (tamper)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)

        if(zone_num < 64 and battery == "yes"):
            device = SatelIntegraBinarySensor(controller, zone_num + 128 +1, zone_name + " (AC KO)" , "problem", CONF_TROUBLE, SIGNAL_TROUBLE_UPDATED)
            devices.append(device)
            device = SatelIntegraBinarySensor(controller, zone_num + 128 + 64 +1 , zone_name + " (battery KO)", "problem", CONF_TROUBLE, SIGNAL_TROUBLE_UPDATED)
            devices.append(device)
            device = SatelIntegraBinarySensor(controller, zone_num+ 128 + 64 + 64 +1, zone_name + " (battery NOT connected)", "problem", CONF_TROUBLE, SIGNAL_TROUBLE_UPDATED)
            devices.append(device)
        

    configured_trouble = discovery_info[CONF_TROUBLE]
    
    for zone_num, device_config_data in configured_trouble.items():
        zone_name = device_config_data[CONF_NAME]
        
        device = SatelIntegraBinarySensor(controller, zone_num + 320, zone_name, "problem", CONF_TROUBLE, SIGNAL_TROUBLE_UPDATED)
        devices.append(device)
    
    configured_keypad = discovery_info[CONF_KEYPAD]
    
    for zone_num, device_config_data in configured_keypad.items():
        zone_name = device_config_data[CONF_NAME]
        
        device = SatelIntegraBinarySensor(controller, zone_num +1+ 64 + 64, zone_name + " (no comm)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)
        device = SatelIntegraBinarySensor(controller, zone_num + 1+64 + 64 + 8, zone_name + " (changed)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)
        device = SatelIntegraBinarySensor(controller, zone_num + 1+64 + 64 + 8 + 8 + 64, zone_name +" (tamper)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)
        device = SatelIntegraBinarySensor(controller, zone_num + 1+64 + 64 + 8 + 8 + 64 + 8, zone_name + " (init ko)", "problem", CONF_TROUBLE2, SIGNAL_TROUBLE2_UPDATED)
        devices.append(device)


    async_add_entities(devices)


class SatelIntegraBinarySensor(SatelIntegraEntity, BinarySensorEntity):
    """Representation of an Satel Integra binary sensor."""

    _attr_should_poll = False

    def __init__(self, controller, device_number, device_name, zone_type, device_type, react_to_signal):
        """Initialize the binary_sensor."""
        super().__init__(controller, device_number, device_name, device_type)
        self._zone_type = zone_type
        self._state = 0
        self._react_to_signal = react_to_signal

    async def async_added_to_hass(self) -> None:
        """Initialize state and register callbacks."""

        # Safely read initial state
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            outputs = getattr(self._satel, "violated_outputs", None)
            if outputs is not None and self._device_number in outputs:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_VIOLATED_UPDATED:
            zones = getattr(self._satel, "violated_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_ALARM_UPDATED:
            zones = getattr(self._satel, "alarm_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_MEM_ALARM_UPDATED:
            zones = getattr(self._satel, "mem_alarm_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_TAMPER_UPDATED:
            zones = getattr(self._satel, "tamper_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_MEM_TAMPER_UPDATED:
            zones = getattr(self._satel, "mem_tamper_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            zones = getattr(self._satel, "bypass_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_MASKED_UPDATED:
            zones = getattr(self._satel, "masked_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_MEM_MASKED_UPDATED:
            zones = getattr(self._satel, "mem_masked_zones", None)
            if zones is not None and self._device_number in zones:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_TROUBLE_UPDATED:
            trouble = getattr(self._satel, "trouble", None)
            if trouble is not None and self._device_number in trouble:
                self._state = 1
            else:
                self._state = 0
                
        elif self._react_to_signal == SIGNAL_TROUBLE2_UPDATED:
            trouble2 = getattr(self._satel, "trouble2", None)
            if trouble2 is not None and self._device_number in trouble2:
                self._state = 1
            else:
                self._state = 0

        # Register dispatcher callback
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._react_to_signal, self._devices_updated
            )
        )

        # Write initial state to HA
        self.async_write_ha_state()

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
        new_state = zones.get(self._device_number, 0)
        if self._state != new_state:
            self._state = new_state
            self.async_write_ha_state()
