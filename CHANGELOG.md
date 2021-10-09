
# GE Home Appliances (SmartHQ) Changelog

## 0.5.0

- Initial support for oven hoods (@digitalbites)
- Added extended mode support for ovens
- Added logic to prevent multiple configurations of the same GE account
- Fixed device info when serial not present (@Xe138)
- Fixed issue with ovens when raw temperature not available (@chadohalloran)
- Fixed issue where Split A/C temperature sensors report UOM incorrectly (@RobertusIT)
- Added convertable drawer mode, proximity light, and interior lights to fridge (@grotto27, @elwing00)
## 0.4.3

- Enabled support for appliances without serial numbers
- Added support for Split A/C units (@RobertusIT)
- Added support for Window A/C units (@mbrentrowe, @swcrawford1)
- Added support for Portable A/C units (@luddystefenson)
- Fixed multiple binary sensors (bad conversion from enum) (@steveredden)
- Fixed delay time interpretation for laundry (@steveredden, @sweichbr)
- Fixed startup issue when encountering an unknown unit type(@chansearrington, @opie546)
- Fixed interpretation of A/C demand response power (@garulf)
- Fixed issues with updating disabled entities (@willhayslett)
- Advantium fixes (@willhayslett)

## 0.4.1

- Fixed an issue with dryer entities causing an error in HA (@steveredden)

## 0.4.0

- Implemented Laundry Support (@warrenrees, @ssindsd)
- Implemented Water Filter Support (@bendavis, @tumtumsback, @rgabrielson11)
- Implemented Initial Advantium Support (@ssinsd)
- Bug fixes for ovens (@TKpizza)
- Additional authentication error handling (@rgabrielson11)
- Additional dishwasher functionality (@ssinsd)
- Introduced new select entity (@bendavis)
- Miscellaneous entity bug fixes/refinements
- Integrated new version of SDK

## 0.3.12

- Initial tracked version