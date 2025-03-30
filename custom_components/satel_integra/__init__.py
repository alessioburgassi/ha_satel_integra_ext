"""Support for Satel Integra devices."""
import collections

from satel_integra2.satel_integra import AsyncSatel
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_PORT, EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.typing import ConfigType

from .const import (
    _LOGGER, DOMAIN, CONF_DEVICE_CODE, CONF_DEVICE_PARTITIONS, CONF_ARM_HOME_MODE,CONF_KEYPAD,CONF_TROUBLE,CONF_TROUBLE2,
    CONF_ZONES, CONF_OUTPUTS, CONF_TEMP_SENSORS, CONF_SWITCHABLE_OUTPUTS, CONF_INTEGRATION_KEY,DEFAULT_ZONE_MASK,CONF_ZOME_MASK,
    DEFAULT_PORT, DEFAULT_CONF_ARM_HOME_MODE, DEFAULT_ZONE_TYPE,CONF_EXPANDER_BATTERY,DEFAULT_EXPANDER_BATTERY,
    DATA_SATEL, CONF_EXPANDER, CONF_DEVICE_CODE, CONF_DEVICE_PARTITIONS, CONF_ARM_HOME_MODE, CONF_ZONE_NAME, CONF_ZONE_TYPE,
    CONF_ZONES,CONF_ZONES_ALARM,CONF_ZONES_MEM_ALARM,CONF_ZONES_TAMPER,CONF_ZONES_MEM_TAMPER,CONF_ZONES_BYPASS,CONF_ZONES_MASKED,CONF_ZONES_MEM_MASKED, CONF_OUTPUTS, CONF_TEMP_SENSORS, CONF_SWITCHABLE_OUTPUTS,CONF_SWITCHABLE_BYPASS, CONF_INTEGRATION_KEY, CONF_TEMP_SENSOR_NAME,
    ZONES, SIGNAL_PANEL_MESSAGE, SIGNAL_VIOLATED_UPDATED, SIGNAL_ALARM_UPDATED, SIGNAL_MEM_ALARM_UPDATED, SIGNAL_TAMPER_UPDATED, SIGNAL_MEM_TAMPER_UPDATED, SIGNAL_BYPASS_UPDATED, SIGNAL_MASKED_UPDATED, SIGNAL_MEM_MASKED_UPDATED,SIGNAL_OUTPUTS_UPDATED,SIGNAL_OUTPUTS_BYPASS_UPDATED,SIGNAL_TROUBLE_UPDATED,SIGNAL_TROUBLE2_UPDATED,
)

ZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE_NAME): cv.string,
        vol.Optional(CONF_ZONE_TYPE, default=DEFAULT_ZONE_TYPE): cv.string,
        vol.Optional(CONF_ZOME_MASK, default=DEFAULT_ZONE_MASK): cv.string,

    }
)
EXPANDER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE_NAME): cv.string,
        vol.Optional(CONF_EXPANDER_BATTERY, default=DEFAULT_EXPANDER_BATTERY): vol.In(
            ["no", "yes"]
        ),
    }
)
KEYPAD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE_NAME): cv.string,
    }
)
TROUBLE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE_NAME): cv.string,
    }
)
EDITABLE_OUTPUT_SCHEMA = vol.Schema({vol.Required(CONF_ZONE_NAME): cv.string})
PARTITION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ZONE_NAME): cv.string,
        vol.Optional(CONF_ARM_HOME_MODE, default=DEFAULT_CONF_ARM_HOME_MODE): vol.In(
            [1, 2, 3]
        ),
    }
)
TEMP_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TEMP_SENSOR_NAME): cv.string,
    }
)

def is_alarm_code_necessary(value):
    """Check if alarm code must be configured."""
    if value.get(CONF_SWITCHABLE_OUTPUTS) and CONF_DEVICE_CODE not in value:
        raise vol.Invalid("You need to specify alarm code to use switchable_outputs")

    return value

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_DEVICE_CODE): cv.string,
                vol.Optional(CONF_DEVICE_PARTITIONS, default={}): {
                    vol.Coerce(int): PARTITION_SCHEMA
                },
                vol.Optional(CONF_ZONES, default={}): {vol.Coerce(int): ZONE_SCHEMA},
                vol.Optional(CONF_OUTPUTS, default={}): {vol.Coerce(int): ZONE_SCHEMA},
                vol.Optional(CONF_EXPANDER, default={}): {vol.Coerce(int): EXPANDER_SCHEMA},
                vol.Optional(CONF_KEYPAD, default={}): {vol.Coerce(int): KEYPAD_SCHEMA},
                vol.Optional(CONF_TROUBLE, default={}): {vol.Coerce(int): TROUBLE_SCHEMA},
                
                vol.Optional(CONF_SWITCHABLE_OUTPUTS, default={}): {
                    vol.Coerce(int): EDITABLE_OUTPUT_SCHEMA
                },
                vol.Optional(CONF_INTEGRATION_KEY, default=''): cv.string,
                vol.Optional(CONF_TEMP_SENSORS, default={}): {vol.Coerce(int): TEMP_SENSOR_SCHEMA},
            },
            is_alarm_code_necessary,
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Satel Integra component."""
    conf = config[DOMAIN]

    zones = conf.get(CONF_ZONES)
    outputs = conf.get(CONF_OUTPUTS)
    switchable_outputs = conf.get(CONF_SWITCHABLE_OUTPUTS)
    expanders = conf.get(CONF_EXPANDER)
    keypad = conf.get(CONF_KEYPAD)
    trouble = conf.get(CONF_TROUBLE)
    
    host = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)
    partitions = conf.get(CONF_DEVICE_PARTITIONS)
    integration_key = conf.get(CONF_INTEGRATION_KEY)

    monitored_outputs = collections.OrderedDict(
        list(outputs.items()) + list(switchable_outputs.items())
    )
    
    configured_trouble = list()
    configured_trouble2 = list()
    
    for zone_num, device_config_data in expanders.items():
        battery = device_config_data[CONF_EXPANDER_BATTERY]
        configured_trouble2.append(zone_num)
        configured_trouble2.append(zone_num + 64)
        configured_trouble2.append(zone_num + 64 + 64 + 8 + 8 + 8)
        if(zone_num < 64 and battery == "yes"):
            configured_trouble.append(zone_num+ 128 + 1)
            configured_trouble.append(zone_num+ 128 + 64 +1)
            configured_trouble.append(zone_num+ 128 + 64 + 64 +1)


    for zone_num, device_config_data in trouble.items():
        configured_trouble.append(zone_num+320)

    for zone_num, device_config_data in keypad.items():
        configured_trouble2.append(zone_num+ 64 + 64)
        configured_trouble2.append(zone_num+ 64 + 64 + 8)
        configured_trouble2.append(zone_num+ 64 + 64 + 8 + 8 + 64)
        configured_trouble2.append(zone_num+ 64 + 64 + 8 + 8 + 64 + 8)


    controller = AsyncSatel(
        host, port, hass.loop, zones, monitored_outputs, partitions, configured_trouble,configured_trouble2) #, integration_key)

    hass.data[DATA_SATEL] = controller

    result = await controller.connect()

    if not result:
        return False

    @callback
    def _close(*_):
        controller.close()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _close)

    _LOGGER.debug("Arm home config: %s, mode: %s ", conf, conf.get(CONF_ARM_HOME_MODE))

    hass.async_create_task(
        async_load_platform(hass, Platform.ALARM_CONTROL_PANEL, DOMAIN, conf, config)
    )

    hass.async_create_task(
        async_load_platform(
            hass,
            Platform.BINARY_SENSOR,
            DOMAIN,
            {CONF_ZONES: zones, CONF_OUTPUTS: outputs,CONF_EXPANDER: expanders, CONF_KEYPAD: keypad, CONF_TROUBLE:trouble},
            config,
        )
    )

    hass.async_create_task(
        async_load_platform(
            hass,
            Platform.SWITCH,
            DOMAIN,
            {
                CONF_SWITCHABLE_OUTPUTS: switchable_outputs,
                CONF_ZONES: zones,
                CONF_DEVICE_CODE: conf.get(CONF_DEVICE_CODE),
            },
            config,
        )
    )

    hass.async_create_task(
        async_load_platform(
            hass,
            Platform.SENSOR,
            DOMAIN,
            {
                CONF_TEMP_SENSORS: conf.get(CONF_TEMP_SENSORS),
            },
            config,
        )
    )
    @callback
    def alarm_status_update_callback():
        """Send status update received from alarm to Home Assistant."""
        _LOGGER.debug("ARM panel state callback")
        async_dispatcher_send(hass, SIGNAL_PANEL_MESSAGE)
    @callback
    def zones_violated_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones VIOLATED callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_VIOLATED_UPDATED, status[ZONES])
    @callback
    def zones_alarm_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones ALARM callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_ALARM_UPDATED, status[ZONES])
    @callback
    def zones_mem_alarm_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones MEMORY ALARM callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_MEM_ALARM_UPDATED, status[ZONES])
    @callback
    def zones_tamper_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones TAMPER callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_TAMPER_UPDATED, status[ZONES])
    @callback
    def zones_mem_tamper_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones MEM TAMPER callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_MEM_TAMPER_UPDATED, status[ZONES])
    @callback
    def zones_bypass_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones BYPASS callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_BYPASS_UPDATED, status[ZONES])
    @callback
    def zones_masked_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones MASK callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_MASKED_UPDATED, status[ZONES])
    @callback
    def zones_mem_masked_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("Zones MEM MASKED callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_MEM_MASKED_UPDATED, status[ZONES])

    @callback
    def outputs_update_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("OUTPUT updated callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_OUTPUTS_UPDATED, status["outputs"])
    @callback
    def trouble_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("TROUBLE callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_TROUBLE_UPDATED, status["trouble"])
    @callback
    def trouble2_callback(status):
        """Update zone objects as per notification from the alarm."""
        _LOGGER.warning("TROUBLE2 callback, status: %s", status)
        async_dispatcher_send(hass, SIGNAL_TROUBLE2_UPDATED, status["trouble2"])
    # Create a task instead of adding a tracking job, since this task will
    # run until the connection to satel_integra is closed.
    hass.loop.create_task(controller.keep_alive())
    hass.loop.create_task(controller.partition_armed_delay())

    hass.loop.create_task(
        controller.monitor_status(
            alarm_status_update_callback, zones_violated_callback, zones_alarm_callback, zones_mem_alarm_callback, zones_tamper_callback,zones_mem_tamper_callback,zones_bypass_callback,zones_masked_callback,zones_mem_masked_callback,outputs_update_callback,trouble_callback,trouble2_callback
        )
    )

    return True
