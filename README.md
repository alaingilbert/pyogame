# pyogame
<img src="https://github.com/alaingilbert/pyogame/blob/develop/logo.png?raw=true" width="300" alt="logo">

OGame is a browser-based, money-management and space-war themed massively multiplayer online browser game with over 
two million accounts.

This lib is supposed to help write scripts and bots for your needs.
it supports ogame_version: `7.6.6`
version `21`

## install
<pre>
pip install ogame
</pre>
update
<pre>
pip install ogame==7.6.6.20
</pre>
dont want to wait for new updates download direct from the develop branch
<pre>
pip install git+https://github.com/alaingilbert/pyogame.git@develop
</pre>

## get started
[Code Snippets](https://github.com/alaingilbert/pyogame/wiki/Code-Snippets)

[Code Style](https://github.com/alaingilbert/pyogame/wiki/Code-Style)

## Discord
[Join Discord](https://discord.gg/CeBDgnR)

## You wanna try a finished bot
[pyogame.net](https://pyogame.net)

## functions
### login
<pre>
from ogame import OGame
from ogame.constants import destination, coordinates, ships, mission, speed, buildings, status
 
empire = OGame(UNI, USER, PASSWORD)

#optional
empire = OGame(UNI, USER, PASSWORD, user_agent='NCSA_Mosaic/2.0 (Windows 3.1)', 
                                    proxy='https://proxy.com:port', 
                                    language='us'
)
</pre>

### test
<pre>
This is a command that will try to run all functions with parameters. 
empire.test()                       returns bool

If this lib is running for long time it is recommended to test it during run time. 
If it fails you can set up a telegram message. A test creates alot of traffic

if not empire.test():
    raise RuntimeWarning("Pyogame test failed, there are functions that dont work anymore. Be Careful")
    # warn the User
</pre>

### get attacked
<pre>
empire.attacked()                   returns bool 
</pre>

### get neutral
<pre>
empire.neutral()                    returns bool 
</pre>

### get friendly
<pre>
empire.friendly()                   returns bool 
</pre>

### get server (universe)
<pre>
server = empire.server()
server.version                      returns str
server.Speed.universe               returns int
server.Speed.fleet                  returns int
server.Donut.galaxy                 returns bool
server.Donut.system                 returns bool
</pre>

### get characterclass
<pre>
Get the class of your Ogame Account['miner', 'explorer', 'warrior', 'none]
empire.character_class()            return string
</pre>

### get rank
<pre>
empire.rank()                       return int
</pre>

### get planet id's
<pre>
empire.planet_ids()                 returns list 

empire.id_by_planet_name('name')    returns int

empire.name_by_planet_id(id)        return string

empire.planet_names()               returns list
</pre>

### get moon id's
<pre>
empire.moon_ids()                   returns list

empire.moon_names()                 returns list

**keep in mind to prefer planets id's moon id dont works on every function**
</pre>

### abandon planet
<pre>
empire.abandon_planet(id)           returns bool

** keep in mind that this is truly final, that no more fleets are needed at the 
departure or destination of this planet and that there is no construction or research underway on it.
</pre>

### rename planet
<pre>
empire.rename_planet(id,'new_name') returns bool

** keep in mind that the name must contain at least two characters **
</pre>

### coordinates
<pre>
coordinates have the format [galaxy, system, position, destination]

destination is referred to planet moon or debris on that coordinate planet=1 debris=2 moon=3
for example [1,200,16,3] = galaxy=1, system=200, position=16, destination=3 for moon
with from ogame.constants import destination the process is much more readable.

when you dont give it an destination it will default to planet

                                        returns list
</pre>
```python
from ogame.constants import coordinates, destination
pos = coordinates(
    galaxy=1,
    system=2,
    position=12,
    dest=destination.debris
)

coordinates(1, 2, 12, destination.moon)
coordinates(1, 2, 12, destination.debris)
coordinates(1, 2, 12, destination.planet) or coordinates(1, 2, 12)
```
### get slot celestials
returns how many planet slots are free to colonize
<pre>
slot = empire.slot_celestial()          returns class
slot.free                               returns int
slot.total                              returns int
</pre>

### get celestial
works with planet's and moon's
<pre>
celestial = empire.celestial(id)        returns class
celestial.temperature                   returns list
celestial.diameter                      returns int
celestial.coordinates                   returns list
celestial.used                          return int
celestial.total                         return int
celestial.free                          return int
</pre>

### get celestial coordinates
works with planet's and moon's
<pre>
empire.celestial_coordinates(id)        returns list
</pre>

### resources
<pre>
resources have the format [metal, crystal, deuterium]
darkmatter & energy are irrelevant, because you cant transport these.
It is used for transport and market functions

from ogame.constants import resources
res = resources(metal=1, crystal=2, deuterium=3)
[1, 2, 3]
</pre>

### get resources
<pre>
empire.resources(id)                    returns class(object)

res = empire.resources(id)
res.resources                           returns resources
res.day_production                      returns resources
res.storage                             returns resources
res.darkmatter                          returns int
res.energy                              returns int
res.metal                               returns int
res.crystal                             returns int
res.deuterium                           returns int
</pre>

### get prices
<pre>
get prices of buildings or ships. Level is mandatory if you pass buildings that exist only once like mines.
</pre>
<pre>
from ogame.constants import price

price(technology, level)                return resources

price(buildings.metal_mine, level=14))
price(ships.deathstar(100))
</pre>


### get supply
<pre>
empire.supply(id)                       returns class(object)

sup = empire.supply(id)

sup.metal_mine.level                    returns int
sup.metal_mine.is_possible              returns bool (possible to build)
sup.metal_mine.in_construction          returns bool
sup.metal_mine.cost                     returns resources

sup.crystal_mine
sup.deuterium_mine
sup.solar_plant
sup.fusion_plant 
sup.metal_storage
sup.crystal_storage
sup.deuterium_storage                   returns class(object)
</pre>

### get facilities
<pre>
empire.facilities(id)                   returns class(object) 

fac = empire.facilities(id)

fac.robotics_factory.level              returns int
fac.robotics_factory.is_possible        returns bool (possible to build)
fac.robotics_factory.in_construction    returns bool

fac.shipyard
fac.research_laboratory
fac.alliance_depot
fac.missile_silo
fac.nanite_factory
fac.terraformer
fac.repair_dock
</pre>

### get moon facilities
<pre>
empire.moon_facilities(id)              returns class(object) 

fac = empire.moon_facilities(id) 
fac.robotics_factory.level              returns int
fac.robotics_factory.is_possible        returns bool (possible to build)
fac.robotics_factory.in_construction    returns bool

fac.shipyard
fac.moon_base
fac.sensor_phalanx 
fac.jump_gate
</pre>

### get traider
<pre>
empire.traider(id)                  returns Exception("function not implemented yet PLS contribute")
</pre>

### get research
<pre>
empire.research(id)                   returns class(object) 

res = empire.research(id)

res.energy.level
res.energy.is_possible
res.energy.in_construction

res.laser
res.ion
res.hyperspace
res.plasma
res.combustion_drive
res.impulse_drive
res.hyperspace_drive
res.espionage
res.computer
res.astrophysics
res.research_network
res.graviton
res.weapons
res.shielding
res.armor
</pre>

### get ships
<pre>
empire.ships(id)                    returns class(object) 

shi = empire.ships(id)

shi.light_fighter.amount
shi.light_fighter.is_possible
shi.light_fighter.in_construction

shi.heavy_fighter
shi.cruiser
shi.battleship
shi.interceptor
shi.bomber
shi.destroyer
shi.deathstar
shi.reaper
shi.explorer
shi.small_transporter
shi.large_transporter
shi.colonyShip
shi.recycler
shi.espionage_probe
shi.solarSatellite
shi.crawler
</pre>

### get defences
<pre>
empire.defences(id)                 returns class(object) 

def = empire.defences(id)

def.rocket_launcher.amount
def.rocket_launcher.is_possible
def.rocket_launcher.in_construction

def.laser_cannon_light
def.laser_cannon_heavy
def.gauss_cannon
def.ion_cannon
def.plasma_cannon
def.shield_dome_small
def.shield_dome_large
def.missile_interceptor
def.missile_interplanetary
</pre>

### get galaxy
<pre>
empire.galaxy(coordinates)          returns list of class(object)
</pre>
```python
for planet in empire.galaxy(coordinates(randint(1,6), randint(1,499))):
    print(planet.list)
    print(planet.name, planet.position, planet.player, planet.player_id, planet.rank, planet.status, planet.moon)
    if status.inactive in planet.status and status.vacation not in planet.status:
        #Farm Inactive
```        

### get ally
<pre>
Returns your current Ally name None if you didnt join one yet

empire.ally()                       returns list
</pre>

### get officers
<pre>
empire.officers()                   returns Exception("function not implemented yet PLS contribute")
</pre>

### get shop
<pre>
empire.shop()                       returns Exception("function not implemented yet PLS contribute")
</pre>

### get slot
<pre>
Get the actual free and total Fleet slots you have available
</pre>
```python
slot = empire.slot_fleet()
slot.fleet.total                     returns int
slot.fleet.free                      returns int
slot.expedition.total                returns int
slot.expedition.free                 returns int
```

### get fleet
<pre>
empire.fleet()                      returns list of class(object)
</pre>

```python
for fleet in empire.fleet():
    if fleet.mission == mission.expedition:
        print(fleet.list)
        print(  
                fleet.id, 
                fleet.mission, 
                fleet.diplomacy, 
                fleet.player, 
                fleet.player_id,
                fleet.returns, 
                fleet.arrival, 
                fleet.origin, 
                fleet.destination
            )
```

### get hostile fleet
<pre>
empire.hostile_fleet()              returns list of class(object)
</pre>

```python
for fleet in empire.hostile_fleet():
    print(fleet.list)
```

### get friendly fleet
<pre>
empire.hostile_fleet()              returns list of class(object)
</pre>

```python
for fleet in empire.friendly_fleet():
    print(fleet.list)
```

### get phalanx
<pre>
~~Dangereous!!! it gets you banned when not valid
empire.phalanx(coordinates, id)     returns list of class(object)~~

</pre>

```python
for fleet in empire.phalanx(moon_id, coordinates(2, 410, 7)):
    if fleet.mission == mission.expedition:
        print(fleet.list)
        print(fleet.id, fleet.mission, fleet.returns, fleet.arrival, fleet.origin, fleet.destination)
```

### get spyreports
<pre>
empire.spyreports()                     returns list of class(object)
empire.spyreports(firstpage=1, lastpage=30)
</pre>

```python
for report in empire.spyreports():
    print(report.fright)
```

### send fleet (for both version 7.6 and 8.0.0)
```python
from ogame.constants import coordinates, mission, speed, fleet
empire.send_fleet(mission=mission.expedition,
                  id=id,
                  where=coordinates(1, 12, 16),
                  ships=fleet(light_fighter=12, bomber=1, cruiser=100),
                  resources=[0, 0, 0],  # optional default no resources
                  speed=speed.max,      # optional default speed.max
                  holdingtime=2)        # optional default 0 will be needed by expeditions
```
<pre>                 
                                        returns bool
</pre>

### return fleet
<pre>
empire.return_fleet(fleet_id):          returns bool

You can't return hostile Fleets :p use the friendly fleet function to avoid confusion.
True if the Fleet you want to return is possible to retreat
</pre>


### send message
<pre>
empire.send_message(player_id, msg)     returns bool
</pre>


### build
Buildings
```python
from ogame.constants import buildings
empire.build(what=buildings.alliance_depot, 
             id=id)

buildings.metal_mine
buildings.crystal_mine
buildings.deuterium_mine
buildings.solar_plant
buildings.fusion_plant
buildings.solar_satellite(int)
buildings.crawler(int)
buildings.metal_storage
buildings.crystal_storage
buildings.deuterium_storage

buildings.robotics_factory
buildings.shipyard
buildings.research_laboratory
buildings.alliance_depot
buildings.missile_silo
buildings.nanite_factory
buildings.terraformer
buildings.repair_dock

empire.build(what=buildings.rocket_launcher(10), 
             id=id)

buildings.rocket_launcher(int)
buildings.laser_cannon_light(int)
buildings.laser_cannon_heavy(int)
buildings.gauss_cannon(int)
buildings.ion_cannon(int)
buildings.plasma_cannon(int)
buildings.shield_dome_small(int)
buildings.shield_dome_large(int)
buildings.missile_interceptor(int)
buildings.missile_interplanetary(int)

buildings.moon_base
buildings.sensor_phalanx
buildings.jump_gate
```
Ships
```python
from ogame.constants import ships
empire.build(what=ships.bomber(10), 
             id=id)

ships.light_fighter(int)
ships.heavy_fighter(int)
ships.cruiser(int)
ships.battleship(int)
ships.interceptor(int)
ships.bomber(int)
ships.destroyer(int)
ships.deathstar(int)
ships.reaper(int)
ships.explorer(int)
ships.small_transporter(int)
ships.large_transporter(int)
ships.colonyShip(int)
ships.recycler(int)
ships.espionage_probe(int)
```
<pre>                 
                                        returns None
</pre>

### do research
```python
from ogame.constants import research
empire.build(what=research.energy, id=id)

research.energy
research.laser
research.ion
research.hyperspace
research.plasma
research.combustion_drive
research.impulse_drive
research.hyperspace_drive
research.espionage
research.computer
research.astrophysics
research.research_network
research.graviton
research.weapons
research.shielding
research.armor
```
<pre>                 
                                        returns None
</pre>

### collect rubble field
<pre> 
this will collect your rubble field at the planet id.
                
empire.collect_rubble_field(id)         returns None
</pre>

### im i still loged In?
<pre>                 
empire.is_logged_in()                   returns Bool
</pre>

### relogin
<pre>                 
empire.relogin()                        returns Bool

switch universes with the same login
empire.relogin('UNI')
</pre>

### keep going
If you are running code for long time you can decorate it with the keep going Decorator. 
If the function gets logged out it will try to relogin and continuing execution.
```python
@empire.keep_going
def run():
    while True:
        print(empire.attacked())
        time.sleep(1)
```

### logout
<pre>                 
empire.logout()                         returns Bool
</pre>
