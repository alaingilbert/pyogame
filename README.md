# OGame



## Installation

`pip install ogame`



## Usage

```py
>>> from ogame import OGame
>>> ogame = OGame('Andromeda', USER, PASW)
>>> ogame.is_under_attack()
True
```



## Methods

### login()

### logout()

### fetch_eventbox():obj

### fetch_resources():obj

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
