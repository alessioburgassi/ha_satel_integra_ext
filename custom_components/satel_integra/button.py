"""Support for Satel Integra modifiable outputs represented as switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import (
    DOMAIN as BUTTON_DOMAIN,
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

from .entity import SatelIntegraEntity
from .const import (
    CONF_OUTPUTS,
    CONF_PARTITIONS,
    CONF_PARTITION_RESET,
    CONF_BUTTON_OUTPUTS,
    CONF_SWITCHABLE_OUTPUTS,
    SIGNAL_PARTITION_RESET_UPDATED,
    SIGNAL_BUTTON_UPDATED,
    CONF_NAME,
    DATA_SATEL,
    CONF_DEVICE_CODE
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Satel Integra switch devices."""
    if not discovery_info:
        return

    # Scrive nel log l'intero contenuto di discovery_info.
    # Usiamo %s per fare in modo che Python converta il dizionario in stringa.
    configured_partitions = discovery_info[CONF_PARTITIONS]
    configured_output = discovery_info[CONF_SWITCHABLE_OUTPUTS]
    controller = hass.data[DATA_SATEL]

    devices = []

    for partition_num, device_config_data in configured_partitions.items():
        name = device_config_data[CONF_NAME] + " Reset"
        
        # Aggiungiamo un log per vedere quali dati vengono letti dalla configurazione
        device = SatelIntegraButton(controller, partition_num,name,discovery_info[CONF_DEVICE_CODE], CONF_PARTITION_RESET,SIGNAL_PARTITION_RESET_UPDATED)
        devices.append(device)
        
    #OUTPUT ADD
    for output_num, device_config_data in configured_output.items():
        name = device_config_data[CONF_NAME]
        try:
            type = device_config_data[CONF_BUTTON_OUTPUTS]
        except KeyError:
            type = "no"
        if type == "yes":
            device = SatelIntegraButton( controller, output_num, name, discovery_info[CONF_DEVICE_CODE],CONF_BUTTON_OUTPUTS,SIGNAL_BUTTON_UPDATED)
            devices.append(device)
            
    async_add_entities(devices)


class SatelIntegraButton(SatelIntegraEntity, ButtonEntity):
    """Representation of an Satel switch."""
    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, controller, button_num,button_name, code, device_type,react_to_signal):
        """Initialize the binary_sensor."""
        super().__init__(controller, button_num, button_name, device_type) # should be "switch")
    
        self._react_to_signal = react_to_signal
        self._code = code

    async def async_press(self) -> None:
        if self._react_to_signal == SIGNAL_PARTITION_RESET_UPDATED:
            _LOGGER.debug("COMMAND PARTITION ALARM RESET name: %s, number: %s", self._name, self._device_number)
            await self._satel.clear_alarm(self._code,[self._device_number])
        if self._react_to_signal == SIGNAL_BUTTON_UPDATED:
            _LOGGER.debug("COMMAND OUTPUT BUTTON ON %s: name: %s, number:%s, turning ON", self._react_to_signal, self._name, self._device_number)
            await self._satel.set_output(self._code, self._device_number, True)
            self.async_write_ha_state()
