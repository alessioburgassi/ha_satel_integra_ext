"""Support for Satel Integra zone states- represented as binary sensors."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .entity import SatelIntegraEntity
from .const import (
    DATA_SATEL,
    CONF_TEMP_SENSORS,
    CONF_TEMP_SENSOR_NAME,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Satel Integra temperature sensor devices."""
    if not discovery_info:
        return

    controller = hass.data[DATA_SATEL]

    async_add_entities(
        [SatelIntegraTemperatureSensor(controller, sensor_num, device_config_data[CONF_TEMP_SENSOR_NAME])
            for sensor_num, device_config_data in discovery_info[CONF_TEMP_SENSORS].items()],
        update_before_add=True)
    async_add_entities([SatelLastEventSensor(hass, entry)])

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=120)
class SatelLastEventSensor(SensorEntity):
    """Sensor che mostra l'ultimo evento letto dalla centrale Satel Integra."""

    _attr_name = "Satel Ultimo Evento"
    _attr_icon = "mdi:timeline-text-outline"
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the sensor."""
        self._hass = hass
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{entry.entry_id}_last_event"
        self._attr_native_value = "Nessun evento rilevato"
        self._attr_extra_state_attributes = {}

    async def async_added_to_hass(self) -> None:
        """Quando l'entità viene aggiunta a HA."""
        async_dispatcher_connect(
            self._hass,
            f"{DOMAIN}_event_updated_{self._entry_id}",
            self._handle_event_update,
        )

    @callback
    def _handle_event_update(self, parsed_event: dict):
        """Aggiorna il sensor quando arriva un nuovo evento."""
        if not parsed_event:
            return

        ts = parsed_event.get("timestamp", "??")
        desc = parsed_event.get("text_long", parsed_event.get("description", "Evento sconosciuto"))
        self._attr_native_value = f"{ts} - {desc[:100]}"

        self._attr_extra_state_attributes = {
            "timestamp": parsed_event.get("timestamp"),
            "event_code": parsed_event.get("event_code"),
            "partition": parsed_event.get("partition"),
            "restore": parsed_event.get("restore"),
            "kkk": parsed_event.get("kkk"),
            "kkk_desc": parsed_event.get("kkk_desc"),
            "source": parsed_event.get("source"),
            "kind": parsed_event.get("kind"),
            "kind_desc": parsed_event.get("kind_desc"),
            "user": parsed_event.get("user"),
            "text_long": parsed_event.get("text_long"),
            "s1": parsed_event.get("s1"),
            "s1_desc": parsed_event.get("s1_desc"),
            "s2": parsed_event.get("s2"),
            "s2_desc": parsed_event.get("s2_desc"),
            "index": parsed_event.get("index"),          # es. "BF0133"
            "index_dec": parsed_event.get("index_dec"),  # es. 12345678
        }

        self.async_write_ha_state()
class SatelIntegraTemperatureSensor(SatelIntegraEntity, SensorEntity):
    """Representation of an Satel Integra temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_should_poll = True

    def __init__(
        self, controller, device_number, device_name
    ):
        """Initialize the sensor."""
        super().__init__(controller, device_number, device_name, "temp")

    async def async_update(self) -> None:
        # generate random temperature between 20.5 and 22.5
        _LOGGER.info("async_update sensor %s", self._device_number)
        import random
        # self._attr_native_value = float(round(random.uniform(20.5, 22.5), 1))

        try:
            self._attr_native_value = await self._satel.read_temp_and_wait(self._device_number)
        except TimeoutError:
            _LOGGER.error("Timeout error while reading temperature %s", self._device_number)
