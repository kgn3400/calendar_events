# Calendar events helper

![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/calendar_events)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/calendar_events/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/calendar_events)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/calendar_events)
[![Validate% with hassfest](https://github.com/kgn3400/calendar_events/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/calendar_events/actions/workflows/hassfest.yaml)

The calendar events helper allows you to create an overall overview for one or more calendars. For a certain number of days into the future and a maximum number of events.

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

## Services

Available services: __reload__

### Service calendar_events.sensor_reload

Reset the Calendar events helper.

