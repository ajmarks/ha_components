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


{% if installed %}
### Changes as compared to your installed version:

#### Breaking Changes

#### Changes

#### Features

{% if version_installed.split('.') | map('int') < '0.4.1'.split('.') | map('int') %}

- Implemented Laundry Support (@warrenrees, @ssindsd)
- Implemented Water Filter Support (@bendavis, @tumtumsback, @rgabrielson11)
- Implemented Initial Advantium Support (@ssinsd)
- Additional authentication error handling (@rgabrielson11)
- Additional dishwasher functionality (@ssinsd)
- Introduced new select entity (@bendavis)
- Integrated new version of SDK

{% endif %}

#### Bugfixes

{% if version_installed.split('.') | map('int') < '0.4.1'.split('.') | map('int') %}

- Bug fixes for ovens (@TKpizza)
- Miscellaneous entity bug fixes/refinements

{% endif %}

{% endif %}
