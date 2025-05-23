[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Alternative Satel Integra Home assistant integration by Alessio Burgassi

The integration is based on build in Home Assistant [Satel Integra integration] (https://www.home-assistant.io/integrations/satel_integra/) and wasilukm version (https://github.com/wasilukm/alt_ha_satel_integra)
It provides the following additional features comparing to the mainstream integration:

  - encrypted communication (see `integration_key` configuration variable)
  - support multiple and concurrent command
  - support all zone status (Violation, Alarm, Memory Alarm, Tamper, Memory Tamper, Mask, Bypass)
  - added switch for bypass any single zone
  - support for panel trouble (AC fail, battery, bus fail, output fail
  - support for expansion trouble (AC fail, battery, tamper, no comm)
  - support for keypad trouble (AC fail, battery, tamper, no comm)
  - added routine to corrent SATEL protocol bug on PANEL ARM/DISARM status message ( when  partition status change Satel send a "status" DISARM for small time and after send correct new status, example WAIT->DISARM->ARM now in HA is reported only corretct WAIT->ARM  (filtered DISARM)
  - support deprecated implementation from 2025.11 HA version


![image](https://github.com/user-attachments/assets/bfe3d604-6570-4336-b157-df5f6f6d807b)



The `satel_integra` integration will allow Home Assistant users who own a Satel Integra alarm panel to leverage their alarm system and its sensors to provide Home Assistant with information about their homes. Connectivity between Home Assistant and the alarm is accomplished through a ETHM extension module that must be installed in the alarm. Compatible with ETHM-1 Plus module with firmware version > 2.00 (version 2.04 confirmed).



There is currently support for the following device types within Home Assistant:

- Binary Sensor: Reports on zone or output statuses
- The integration create one binary sensor for each status (violated, alarm, tamper etc)
- Switch: allows for setting states of selected outputs 
- Alarm Control Panel: represents the partition. Reports its status, and can be used to arm/disarm the partition

The module communicates via Satel's open TCP protocol published on their website. It subscribes for new events coming from alarm system and reacts to them immediately.

## Setup

Please note that **ETHM-1 module is currently not supported**: it does not provide functionality used by this extension. At the moment only ETHM-1 Plus module is supported. That might change in the future, but no promises are given.

A list of all partition, zone and output IDs can be acquired by running DloadX program and connecting to your alarm.

For the Binary Sensor check the [type/class](https://www.home-assistant.io/integrations/binary_sensor/) list for a possible visualization of your zones. Note: If no zones or outputs are specified, Home Assistant will not load any binary_sensor components.

### Manual installation
 - copy `custom_componetns/satel_integra` to your Home Assistant configuration folder
 - update `configuration.yaml` (see below)
 - restart Home Assistant

### Installation with HACS

 - add the repository (https://github.com/alessioburgassi/ha_satel_integra_ext) to the [HACS custom repositories](https://hacs.xyz/docs/faq/custom_repositories)
 - in HACS look for Satel Integra and install the integration
 - update `configuration.yaml` (see below)
 - restart Home Assistant

### Removal

Uninstall in HACS or manually remove `satel_integra` folder from `custom_components`. After this, restart Home Assistant.

Please note that `Alternative Satel Integra` overrides core `Satel Integra`, so after removal the core integration
will start working. To avoid this, remove `satel_integra` entries from `configuration.yaml`

## Configuration

The configuration is compatible with the original [Satel Integra](https://www.home-assistant.io/integrations/satel_integra/). Therefore, migration to `Alternative Satel Integra`
doesn't require any modifications unless a user wants to use new features.

A `satel_integra` section must be present in the `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
satel_integra:
  host: IP_ADDRESS
```

### Configuration Variables
#### host
The IP address of the Satel Integra ETHM module on your home network, if using socket type.
  - *required*: true
  - *default*: localhost
  - *type*: string

#### port
The port on which the ETHM module listens for clients using integration protocol.
  - *required*: false
  - *default*: 7094
  - *type*: integer

#### code
User password, it's needed for making use of the switchable_outputs. It's recommended not to use admin password.
  - *required*: false
  - *type*: string

#### integration_key
Integration key for encrypted communication. If not specified then communication will not be encrypted.
Set the same value as configured in Satel Integra system (check manual for more information)

  - *required*: false
  - *type*: string


#### partitions
List of the partitions to operate on.
  - *required*: false
  - *type*: [integer, list]

        
&nbsp;&nbsp;&nbsp;&nbsp;**name**

&nbsp;&nbsp;&nbsp;&nbsp;Name of the partition.

- *required*: true
- *type*: string

&nbsp;&nbsp;&nbsp;&nbsp;**arm_home_mode**

&nbsp;&nbsp;&nbsp;&nbsp;The mode in which the partition is armed when 'arm home' is used. Possible options are `1`,`2` or `3`.

&nbsp;&nbsp;&nbsp;&nbsp;For more information on what the differences are between them, please refer to Satel Integra manual.

  - *required*: false
  - *default*: 1
  - *type*: integer

#### zones
This parameter lists the zones (or inputs) that will be visible by Home Assistant. For each zone, a proper ID must be given as well as its name. The name is arbitrary and does not need to match the one specified in Satel Integra alarm configuration.

  - *required*: false
  - *type*: [integer, list]

&nbsp;&nbsp;&nbsp;&nbsp;**name**

&nbsp;&nbsp;&nbsp;&nbsp;Name of the zone.

  - *required*: true
  - *type*: string

&nbsp;&nbsp;&nbsp;&nbsp;**type**

&nbsp;&nbsp;&nbsp;&nbsp;The zone type.

  - *required*: false
  - *default*: motion
  - *type*: string

#### outputs
Very similar to zones, but with outputs. Satel Integra uses outputs to inform external systems about different events. For example power failure, or that alarm started counting for exit or some other user-defined condition. They may be used for simple alarm-based automation. For more information please refer to Satel homepage and forums.

  - *required*: false
  - *type*: [integer, list]

&nbsp;&nbsp;&nbsp;&nbsp;**name**

&nbsp;&nbsp;&nbsp;&nbsp;Name of the output.

  - *required*: true
  - *type*: string

&nbsp;&nbsp;&nbsp;&nbsp;**type**

&nbsp;&nbsp;&nbsp;&nbsp;The type of the device - just for presentation.

  - *required*: false
  - *default*: motion
  - *type*: string

#### switchable_outputs
Switchable outputs. These will show up as switches within Home Assistant.

  - *required*: false
  - *type*: [integer, list]

&nbsp;&nbsp;&nbsp;&nbsp;**name**

&nbsp;&nbsp;&nbsp;&nbsp;Name of the output.

  - *required*: true
  - *type*: string

## Full examples

```yaml
# Example configuration.yaml entry
satel_integra:
  host: 192.168.1.200
  port: 7094
  code: 1234
  partitions:
    01:
      name: "Home"
      arm_home_mode: 2
    02:
      name: "Garden"
  zones:
    01:
      name: "Riv taverna"
      type: "motion"
      mask: "yes"
    02:
      name: "Porta rampa"
      type: "opening"
    06:
      name: "Fumo locale tecnico"
      type: "smoke"
    22:
      name: "Porta ingresso"
      type: "opening"

  outputs:
    35:
      name: "Sirena"
      type: "safety"

  switchable_outputs:
    235:
      name: "Kitchen"
    237:
      name: "Forno"
  expander:
    0:
      name: "Exp bus 1 number 0"
      battery: "yes"
    1:
      name: "Exp bus 1 number 1"   
    32:
      name: "Exp bus 2 number 0"    
    33:
      name: "Exp bus 2 number 1"     
  trouble:
    1:
      name: "Alarm OUT 1 fault"
    2:
      name: "Alarm OUT 2 fault"
    3:
      name: "Alarm OUT 3 fault"
    4:
      name: "Alarm OUT 4 fault"
    5:
      name: "Alarm +KPD fault"
    6:
      name: "Alarm +EX1 +EX2 fault"
    7:
      name: "Alarm Battery fault"
    8:
      name: "Alarm AC fault"
    9:
      name: "Alarm Bus DT1 fault"
    10:
      name: "Alarm Bus DT2 fault"
    11:
      name: "Alarm Bus DTM fault"
    12:
      name: "Alarm time fault"
    13:
      name: "Alarm No DTR Signal"
    14:
      name: "Alarm battery not present"
  keypad:
    0:
      name: "keypad 0"
    1:
      name: "Keypad 1"
      
