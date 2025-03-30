import logging

_LOGGER = logging.getLogger(__package__)

DOMAIN = "satel_integra"

DEFAULT_ALARM_NAME = "satel_integra"
DEFAULT_PORT = 7094
DEFAULT_CONF_ARM_HOME_MODE = 1
DEFAULT_DEVICE_PARTITION = 1
DEFAULT_ZONE_TYPE = "motion"
DEFAULT_EXPANDER_BATTERY = "no"
DEFAULT_ZONE_MASK = "no"
DATA_SATEL = "satel_integra"

CONF_DEVICE_CODE = "code"
CONF_DEVICE_PARTITIONS = "partitions"
CONF_ARM_HOME_MODE = "arm_home_mode"
CONF_ZONE_NAME = "name"
CONF_EXPANDER_BATTERY = "battery"
CONF_ZOME_MASK ="mask"
CONF_EXPANDER ="expander"
CONF_KEYPAD ="keypad"
CONF_TROUBLE ="trouble"
CONF_TROUBLE2 ="trouble2"

CONF_ZONE_TYPE = "type"
CONF_ZONES = "zones"
CONF_ZONES_ALARM = "zones_alarm"
CONF_ZONES_MEM_ALARM = "zones_mem_alarm"
CONF_ZONES_TAMPER = "zones_tamper"
CONF_ZONES_MEM_TAMPER = "zones_mem_tamper"
CONF_ZONES_BYPASS = "zones_bypass"
CONF_ZONES_MASKED = "zones_masked"
CONF_ZONES_MEM_MASKED = "zones_mem_masked"

CONF_OUTPUTS = "outputs"
CONF_TEMP_SENSORS = "temperature_sensors"
CONF_SWITCHABLE_OUTPUTS = "switchable_outputs"
CONF_SWITCHABLE_BYPASS = "switchable_bypass"
CONF_INTEGRATION_KEY = "integration_key"
CONF_TEMP_SENSOR_NAME = "name"
ZONES = "zones"
SIGNAL_PANEL_MESSAGE = "satel_integra.panel_message"
SIGNAL_PANEL_ARM_AWAY = "satel_integra.panel_arm_away"
SIGNAL_PANEL_ARM_HOME = "satel_integra.panel_arm_home"
SIGNAL_PANEL_DISARM = "satel_integra.panel_disarm"

SIGNAL_VIOLATED_UPDATED = "satel_integra.zones_violated"
SIGNAL_ALARM_UPDATED = "satel_integra.zones_alarm"
SIGNAL_MEM_ALARM_UPDATED = "satel_integra.zones_mem_alarm"
SIGNAL_TAMPER_UPDATED = "satel_integra.zones_tamper"
SIGNAL_MEM_TAMPER_UPDATED = "satel_integra.zones_mem_tamper"
SIGNAL_BYPASS_UPDATED = "satel_integra.zones_bypass"
SIGNAL_MASKED_UPDATED = "satel_integra.zones_masked"
SIGNAL_MEM_MASKED_UPDATED = "satel_integra.zones_mem_masked"

SIGNAL_OUTPUTS_UPDATED = "satel_integra.outputs_updated"

SIGNAL_OUTPUTS_BYPASS_UPDATED = "satel_integra.outputs_bypass_updated"

SIGNAL_TROUBLE_UPDATED = "satel_integra.trouble_updated"
SIGNAL_TROUBLE2_UPDATED = "satel_integra.trouble2_updated"
