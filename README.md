# OGame



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
>>> from ogame.constants import Ships, Speed, Missions
>>> ships = [(Ships['SmallCargo'], 10), (Ships['LargeCargo'], 50), (Ships['Cruiser'], 40)]
>>> speed = Speed['100%']
>>> where = {'galaxy': 9, 'system': 9, 'position': 9}
>>> mission = Missions['Transport']
>>> resources = {'metal': 10000, 'crystal': 20000, 'deuterium': 12000}
>>> ogame.send_fleet('xxxxxxxx', ships, speed, where, mission, resources)
```

###### Build things example

```py
>>> ogame.build('xxxxxxxx', (Ships['SmallCargo'], 10))
>>> ogame.build('xxxxxxxx', (Defense['RocketLauncher'], 100))
>>> ogame.build('xxxxxxxx', Buildings['MetalMine'])
>>> ogame.build('xxxxxxxx', Research['GravitonTechnology'])
```

###### Get resources example

```py
>>> ogame.get_resources('xxxxxxxx')
{'metal': 10000, 'crystal': 20000, 'deuterium': 30000}
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

### build_defense(planet_id:int, defense_id:int, nbr:int)

### build_ships(planet_id:int, ship_id:int, nbr:int)

### build_building(planet_id:int, building_id:int)

### build_technology(planet_id:int, technology_id:int)

### send_fleet(planet_id:int, ships:array.<tuple>, speed:int, where:obj, mission:int, resources:obj)

### get_url(name:string[, planet_id:int]):string

### get_servers(domain:string):obj

### get_universe_url(universe:string):string



## Exceptions

Ogame.errors

### BAD_USERNAME_PASSWORD

### NOT_LOGGED

### NOT_ENOUGH_RESOURCES

### MISSING_TECH_DEPENDENCIES

### BAD_UNIVERSE_NAME



## Author

Alain Gilbert ([@alain_gilbert](http://twitter.com/alain_gilbert))
