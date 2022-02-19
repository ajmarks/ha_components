# GE Home Appliances (SmartHQ)

Integration for GE WiFi-enabled appliances into Home Assistant.  This integration currently support the following devices:

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


{% if installed %}
### Changes as compared to your installed version:

#### Breaking Changes

{% if version_installed.split('.') | map('int') < '0.6.0'.split('.') | map('int') %}
- Requires HA version 2021.12.0 or later
- Enabled authentication to both US and EU regions (may require re-auth)
- Changed the sensors to use native value/uom
- Changed the temperatures to always be natively fahrenheit (API appears to always use this system) (@vignatyuk) 
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.0'.split('.') | map('int') %}
- Laundry support changes will cause entity names to be different, you will need to fix in HA (uninstall, reboot, delete leftover entitites, install, reboot)
{% endif %}

#### Changes

{% if version_installed.split('.') | map('int') < '0.5.0'.split('.') | map('int') %}
- Added logic to prevent multiple configurations of the same GE account
{% endif %}

#### Features

{% if version_installed.split('.') | map('int') < '0.6.0'.split('.') | map('int') %}
- Initial support for Water Softeners (@npentell, @drjeff)
- Initial support for Opal Ice Makers (@mbcomer, @knobunc)
- Initial support for Microwaves (@mbcomer, @mnestor)
- Initial support for Coffee Makers (@alexanv1)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.5.0'.split('.') | map('int') %}
- Support for Oven Hood units (@digitalbites)
- Added extended mode support for ovens
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.3'.split('.') | map('int') %}
- Support for Portable, Split, and Window AC units (@swcrawford1, @mbrentrowe, @RobertusIT, @luddystefenson)
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

{% if version_installed.split('.') | map('int') < '0.6.0'.split('.') | map('int') %}
- Updated deprecated icons (@mjmeli, @schmittx)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.5.0'.split('.') | map('int') %}
- Advantium fixes (@willhayslett)
- Fixed device info when serial not present (@Xe138)
- Fixed issue with ovens when raw temperature not available (@chadohalloran)
- Fixed issue where Split A/C temperature sensors report UOM incorrectly (@RobertusIT)
- Added convertable drawer mode, proximity light, and interior lights to fridge (@groto27, @elwing00)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.3'.split('.') | map('int') %}
- Bug fixes for laundry (@steveredden, @sweichbr)
- Fixed startup issue when encountering an unknown unit type(@chansearrington, @opie546)
- Fixed interpretation of A/C demand response power (@garulf)
- Fixed issues with updating disabled entities (@willhayslett)
- Advantium fixes (@willhayslett)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.1'.split('.') | map('int') %}
- Fixed an issue with dryer entities causing an error in HA (@steveredden)
{% endif %}

{% if version_installed.split('.') | map('int') < '0.4.0'.split('.') | map('int') %}
- Bug fixes for ovens (@TKpizza)
- Miscellaneous entity bug fixes/refinements
{% endif %}

{% endif %}
