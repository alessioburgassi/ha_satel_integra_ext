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
    CONF_DEVICE_PARTITIONS,
    CONF_PARTITION_RESET,
    CONF_ZONE_NAME,
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
    _LOGGER.info("Contenuto di discovery_info: %s", discovery_info)

    configured_partitions = discovery_info[CONF_DEVICE_PARTITIONS]
    controller = hass.data[DATA_SATEL]

    devices = []

    for partition_num, device_config_data in configured_partitions.items():
        zone_name = device_config_data[CONF_ZONE_NAME]
        
        # Aggiungiamo un log per vedere quali dati vengono letti dalla configurazione
        _LOGGER.debug("Creazione in corso per reset partizione %s (Nome: %s)", partition_num, zone_name)
        device = SatelIntegraButton(controller, partition_num,discovery_info[CONF_DEVICE_CODE],zone_name + " Reset", CONF_PARTITION_RESET)
        devices.append(device)

    async_add_entities(devices)


class SatelIntegraButton(SatelIntegraEntity, ButtonEntity):
    """Representation of an Satel switch."""
    _attr_has_entity_name = False
    _attr_should_poll = False

    def __init__(self, controller, partition_num, code, partition_name, device_type):
        """Initialize the binary_sensor."""
        super().__init__(controller, partition_num, partition_name, device_type) # should be "switch")
        self._state = False
        self._device_number = partition_num
        self._device_type = device_type
        self._code = code

    async def async_press(self) -> None:
        _LOGGER.debug( "COMMAND BUTTON PRESSED: name: %s  number %s: type:%s", self._name, self._device_number, self._device_type)
        await self._satel.clear_alarm(self._code,[self._device_number])
        
