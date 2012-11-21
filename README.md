![](http://images2.wikia.nocookie.net/__cb20101218084357/ogame/images/c/c9/Logo.png)

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

###### Get cost informations example

```py
>>> ogame.get_cost(PLANET_ID, Defense['RocketLauncher'])
{'metal': 2000, 'crystal': 0, 'deuterium': 0, 'time': 23}
```

## Methods

### login()

### logout()

### fetch_eventbox():obj

### fetch_resources():obj

### get_resources(planet_id:int):obj

### is_under_attack():bool

### get_planet_ids():array.<int>

### get_planet_by_name(name:string):int

### build(planet_id:int, arg:*)

### send_fleet(planet_id:int, ships:array.<tuple>, speed:int, where:obj, mission:int, resources:obj)

### cancel_fleet(fleet_id:string)

### get_fleet_ids():array.<string>



## Author

Alain Gilbert ([@alain_gilbert](http://twitter.com/alain_gilbert))
