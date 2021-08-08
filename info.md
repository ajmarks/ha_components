# GE Home Appliances (SmartHQ)

Integration for GE WiFi-enabled appliances into Home Assistant.  This integration currently support the following devices:

- Fridge 
- Oven
- Dishwasher 
- Laundry (Washer/Dryer)
- Whole Home Water Filter
- Advantium

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


{% if installed %}
### Changes as compared to your installed version:

#### Breaking Changes

{% if version_installed.split('.') | map('int') < '0.4.0'.split('.') | map('int') %}
- Laundry support changes will cause entity names to be different, you will need to fix in HA (uninstall, reboot, delete leftover entitites, install, reboot)
{% endif %}

#### Changes

#### Features

{% if version_installed.split('.') | map('int') < '0.4.3'.split('.') | map('int') %}
- Support for Split and Window AC units (@swcrawford1, @mbrentrowe, @RobertusIT)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.0'.split('.') | map('int') %}
- Implemented Laundry Support (@warrenrees, @ssindsd)
- Implemented Water Filter Support (@bendavis, @tumtumsback, @rgabrielson11)
- Implemented Initial Advantium Support (@ssinsd)
- Additional authentication error handling (@rgabrielson11)
- Additional dishwasher functionality (@ssinsd)
- Introduced new select entity (@bendavis)
- Integrated new version of SDK
{% endif %}

#### Bugfixes

{% if version_installed.split('.') | map('int') < '0.4.3'.split('.') | map('int') %}
- Bug fixes for laundry (@steveredden, @sweichbr)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.1'.split('.') | map('int') %}
- Fixed an issue with dryer entities causing an error in HA (@steveredden)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.0'.split('.') | map('int') %}
- Bug fixes for ovens (@TKpizza)
- Miscellaneous entity bug fixes/refinements
{% endif %}

{% endif %}
