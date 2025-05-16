"""Support for Satel Integra modifiable outputs represented as switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .entity import SatelIntegraEntity
from . import (
    CONF_DEVICE_CODE,
    CONF_SWITCHABLE_OUTPUTS,
    CONF_SWITCHABLE_BYPASS,
    CONF_ZONE_NAME,
    CONF_ZONES,
    DATA_SATEL,
    SIGNAL_OUTPUTS_UPDATED,
    SIGNAL_BYPASS_UPDATED
)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["satel_integra"]


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Satel Integra switch devices."""
    if not discovery_info:
        return

    configured_output = discovery_info[CONF_SWITCHABLE_OUTPUTS]
    configured_zones = discovery_info[CONF_ZONES]
    controller = hass.data[DATA_SATEL]

    devices = []

    for zone_num, device_config_data in configured_output.items():
        zone_name = device_config_data[CONF_ZONE_NAME]

        device = SatelIntegraSwitch(
            controller, zone_num, zone_name, discovery_info[CONF_DEVICE_CODE],CONF_SWITCHABLE_OUTPUTS,SIGNAL_OUTPUTS_UPDATED
        )

        devices.append(device)
#BYPASS ADD
    for output_num, device_config_data in configured_zones.items():
        output_name = device_config_data[CONF_ZONE_NAME] + ' (bypass)' 

        device = SatelIntegraSwitch(
            controller, output_num, output_name, discovery_info[CONF_DEVICE_CODE], CONF_SWITCHABLE_BYPASS, SIGNAL_BYPASS_UPDATED
        )
        devices.append(device)



    async_add_entities(devices)


class SatelIntegraSwitch(SatelIntegraEntity, SwitchEntity):
    """Representation of an Satel switch."""

    _attr_should_poll = False

    def __init__(self, controller, device_number, device_name, code, device_type, react_to_signal):
        """Initialize the binary_sensor."""
        super().__init__(controller, device_number, device_name, device_type) # should be "switch")
        self._state = False
        self._code = code
        
        self._device_type = device_type
        self._react_to_signal = react_to_signal


    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            async_dispatcher_connect(
                self.hass, SIGNAL_OUTPUTS_UPDATED, self._devices_updated
            )
        
        if self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            async_dispatcher_connect(
                self.hass, SIGNAL_BYPASS_UPDATED, self._devices_updated_bypass
            )

    @callback
    def _devices_updated(self, zones):
        """Update switch state, if needed."""
        if self._device_number in zones:
            new_state = self._read_state()
            if new_state != self._state:
                self._state = new_state
                self.async_write_ha_state()
            _LOGGER.debug("SWITCH UPDATE STATUS name: %s, number:%s, old_state:%s, new_state:%s zones: %s", self._name,self._device_number,self._state,new_state, zones)
    @callback
    def _devices_updated_bypass(self, zones):
        """Update switch state, if needed."""
        if self._device_number in zones:
            new_state = self._read_state()
            
            if new_state != self._state:
                self._state = new_state
                self.async_write_ha_state()
            _LOGGER.debug("BYPASS SWITCH UPDATE STATUS name: %s, number:%s, old_state:%s, new_state:%s zones: %s", self._name,self._device_number,self._state,new_state, zones)
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            _LOGGER.debug("COMMAND SWITCH ON %s: name: %s  number %s: type:%s status: %s, turning ON",self._react_to_signal, self._name,self._device_number, self._device_type, self._state)
        
            await self._satel.set_output(self._code, self._device_number, True)
            self.async_write_ha_state()
        if self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            _LOGGER.debug("COMMAND ZONE BYPASS %s: name: %s  number %s: type:%s status: %s, turning ON",self._react_to_signal, self._name,self._device_number, self._device_type, self._state)
            await self._satel.set_bypass(self._code, self._device_number, True)
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            _LOGGER.debug("COMMAND SWITCH OFF %s: name: %s  number %s: type:%s status: %s, turning OFF",self._react_to_signal, self._name,self._device_number, self._device_type, self._state)
            await self._satel.set_output(self._code, self._device_number, False)
            self.async_write_ha_state()
        if self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            _LOGGER.debug("COMMAND ZONE UN-BYPASS %s: name: %s  number %s: type:%s status: %s, turning OFF",self._react_to_signal, self._name,self._device_number, self._device_type, self._state)
        
            await self._satel.set_bypass(self._code, self._device_number, False)
            self.async_write_ha_state()

    @property
    def is_on(self):
        """Return true if device is on."""
        self._state = self._read_state()
        return self._state

    def _read_state(self):
        """Read state of the device."""
        if self._react_to_signal == SIGNAL_OUTPUTS_UPDATED:
            return self._device_number in self._satel.violated_outputs
        if self._react_to_signal == SIGNAL_BYPASS_UPDATED:
            return self._device_number in self._satel.bypass_zones
