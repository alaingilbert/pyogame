![](http://images2.wikia.nocookie.net/__cb20101218084357/ogame/images/c/c9/Logo.png)



## Intro

[ogame.org](http://ogame.org) is a strategy-game set in space.
Thousands of players across the world compete at the same time.
In order to play you only need a web browser.

This library is meant to let you create scripts that will automate
many tasks. For example, you could create a script that will protect
your fleets when you're not in front of your computer.

You could also create a completely automated player ! Enjoy !



## Installation

`pip install ogame`



## Usage

###### Verify attack example

```py
>>> from ogame import OGame
>>> ogame = OGame('Andromeda', USER, PASW)
>>> ogame.is_under_attack()
True
```

###### Send fleet example

```py
>>> from ogame.constants import Ships, Speed, Missions, Buildings, Research, Defense
>>> ships = [(Ships['SmallCargo'], 10), (Ships['LargeCargo'], 50), (Ships['Cruiser'], 40)]
>>> speed = Speed['100%']
>>> where = {'galaxy': 9, 'system': 9, 'position': 9}
>>> mission = Missions['Transport']
>>> resources = {'metal': 10000, 'crystal': 20000, 'deuterium': 12000}
>>> ogame.send_fleet(PLANET_ID, ships, speed, where, mission, resources)
```

###### Build things example

```py
>>> ogame.build(PLANET_ID, (Ships['SmallCargo'], 10))
>>> ogame.build(PLANET_ID, (Defense['RocketLauncher'], 100))
>>> ogame.build(PLANET_ID, [(Defense['RocketLauncher'], 100), (Defense['LightLaser'], 500)])
>>> ogame.build(PLANET_ID, Buildings['MetalMine'])
>>> ogame.build(PLANET_ID, Research['GravitonTechnology'])
```

###### Get resources example

```py
>>> ogame.get_resources(PLANET_ID)
{'metal': 3000, 'crystal': 2000, 'deuterium': 1000, 'energy': 686, 'darkmatter': 700}
```



## Methods

### login()

### logout()

### is_logged():bool

### get_page_content([page=overview:string]):string

### fetch_eventbox():obj

### fetch_resources():obj

### get_resources(planet_id:int):obj

### get_ships(planet_id:int):obj

```
{'EspionageProbe': 0, 'Destroyer': 0, 'LightFighter': 0, 'ColonyShip': 0, 'Deathstar': 0,
 'HeavyFighter': 0, 'LargeCargo': 0, 'Cruiser': 0, 'Recycler': 0, 'Battleship': 0,
 'Battlecruiser': 0, 'Bomber': 0, 'SolarSatellite': 0, 'SmallCargo': 0}
```

### is_under_attack():bool

### get_planet_ids():array.\<string\>

### get_planet_by_name(name:string):int

### build(planet_id:int, arg:*)

### send_fleet(planet_id:int, ships:array.\<tuple\>, speed:int, where:obj, mission:int, resources:obj)

### cancel_fleet(fleet_id:string)

### get_fleet_ids():array.\<string\>

### get_server_time():obj



## Author

Alain Gilbert ([@alain_gilbert](http://twitter.com/alain_gilbert))
