# GE Home Appliances (SmartHQ)

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

Integration for GE WiFi-enabled appliances into Home Assistant.  This integration currently supports the following devices:

- Fridge
- Oven
- Dishwasher 
- Laundry (Washer/Dryer)
- Whole Home Water Filter
- Whole Home Water Softener
- A/C (Portable, Split, Window)
- Range Hood
- Advantium
- Microwave
- Opal Ice Maker
- Coffee Maker

**Forked from Andrew Mark's [repository](https://github.com/ajmarks/ha_components).**

## Home Assistant UI Examples 
Entities card:

![Entities](https://raw.githubusercontent.com/simbaja/ha_components/master/img/appliance_entities.png)

Fridge Controls:

![Fridge controls](https://raw.githubusercontent.com/simbaja/ha_components/master/img/fridge_control.png)

Oven Controls:

![Fridge controls](https://raw.githubusercontent.com/simbaja/ha_components/master/img/oven_controls.png)

A/C Controls:

![A/C controls](https://raw.githubusercontent.com/simbaja/ha_components/master/img/ac_controls.png)

## Installation (Manual)

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `ge_home`.
4. Download _all_ the files from the `custom_components/ge_home/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "GE Home"

## Installation (HACS)

Please follow directions [here](https://hacs.xyz/docs/faq/custom_repositories/), and use https://github.com/simbaja/ha_gehome as the repository URL.
## Configuration

Configuration is done via the HA user interface.

## Change Log

Please click [here](CHANGELOG.md) for change information.

[commits-shield]: https://img.shields.io/github/commit-activity/y/simbaja/ha_gehome.svg?style=for-the-badge
[commits]: https://github.com/simbaja/ha_gehome/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/simbaja/ha_gehome.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Jack%20Simbach%20%40simbaja-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/simbaja/ha_gehome.svg?style=for-the-badge
[releases]: https://github.com/simbaja/ha_gehome/releases