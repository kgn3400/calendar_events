# Calendar events helper

![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/calendar_events)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/calendar_events/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/calendar_events)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/calendar_events)
[![Validate% with hassfest](https://github.com/kgn3400/calendar_events/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/calendar_events/actions/workflows/hassfest.yaml)

The Calendar events helper integration allows you to create a binary_sensor or sensor which rotate through a set of the same type of entities with a user defined time interval. if the binary_sensors/sensors set has the same attribute, it's possible to use cards which support showing attributes.

For installation instructions until the Calendar events helper is part of HACS, [see this guide](https://hacs.xyz/docs/faq/custom_repositories).

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=calendar_events)

## Configuration

Configuration is setup via UI in Home assistant. To add one, go to [Settings > Devices & Services > Helpers](https://my.home-assistant.io/redirect/helpers) and click the add button. Next choose the [Calendar events helper](https://my.home-assistant.io/redirect/config_flow_start?domain=calendar_events) option.

<!-- <img src="images/config.png" width="400" height="auto" alt="Config"> -->
<!--
<img src="https://github.com/kgn3400/calendar_events/blob/main/images/config.png" width="400" height="auto" alt="Config">
<br/>
<br/>
-->
It's possible to synchronize the rotation between multiple carousels by using the same optional Timer helper. Restarting the Timer helper can be done via the Calendar events helper or via an automation

The optional 'show if template' config settings is used to decide if the entity should be shown. The evaluated result should be True for the entity to be included in calendar_events rotation. Template values = state and dict state_attributes.
If there is no entities to show, then the Calendar events entity state will be set to unknown. And the state can be used in the conditional card to decide if the card should be shown.

## Services

Available services: __add__, __remove__, __show_entity__, __show_next__ and __show_prev__

### Service calendar_events.binary_sensor_add/calendar_events.sensor_add

Add entity to Calendar events helper.

### Service calendar_events.binary_sensor_remove/calendar_events.sensor_remove

Remove entity from Calendar events helper.

### Service calendar_events.binary_sensor_show_next/calendar_events.sensor_show_next

Show next entity in Calendar events helper.

### Service calendar_events.binary_sensor_show_prev/calendar_events.sensor_show_prev

Show previous ext entity in Calendar events helper.
