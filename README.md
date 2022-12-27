 # pyogame
<img src="https://github.com/alaingilbert/pyogame/blob/develop/logo.png?raw=true" width="300" alt="logo">

OGame is a browser-based, money-management and space-war themed massively multiplayer online browser game with over 
two million accounts.

This lib is supposed to help write scripts and bots for your needs.
it supports ogame_version: `8.4.0`
version `22`

## install
<pre>
pip install ogame
</pre>
update
<pre>
pip install ogame==8.4.0.22
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

### get highscore-list
<pre>
empire.highscore(page=1)            return list

Page 1 returns the data of all Players in Top 100
Each list entry consists of a separate class 

player_top1 = empire.highscore(page=1)[0]
player_top1.name                    return str
player_top1.player_id               return int
player_top1.rank                    return int
player_top1.points                  return int
player_top1.list                    return list [name, player_id, rank, points]

makes tracking player-progress through the highscore possible 
</pre>

### get characterclass
<pre>
Get the class of your Ogame Account['miner', 'explorer', 'warrior', 'none]
empire.character_class()            return string
</pre>

### chose characterclass
<pre>
from ogame.constants import character_class
empire.choose_character_class(
    character_class.miner
)                                   return bool
</pre>

### get rank
<pre>
empire.rank()                       return int
</pre>

### get planet id's
<pre>
empire.planet_ids()                 return list 

empire.planet_names()               return list

empire.planet_coords()              return list

empire.id_by_planet_name('name')    return int
empire.name_by_planet_id(id)        return string

empire.planet_infos()               return list of class
planet1 = empire.planet_infos()[0]  return class

planet1.coordinates                 return list
planet1.temperature                 return list
planet1.diameter                    return int
planet1.used                        return int
planet1.total                       return int
planet1.free                        return int

useful for importing all celestial data of all planets
at once through loading one single overview page
</pre>

### get moon id's
<pre>
empire.moon_ids()                   return list

empire.moon_names()                 return list

empire.moon_coords()                return list

empire.id_by_moon_name('name')      return int
empire.name_by_moon_id(id)          return string

empire.moon_infos()                 return list of class
moon1 = empire.moon_infos()[0]      return class

moon1.coordinates                   return list
moon1.temperature                   return list
moon1.diameter                      return int
moon1.used                          return int
moon1.total                         return int
moon1.free                          return int

useful for importing all celestial data of all moons
at once through loading one single overview page
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

### get extra_slots
returns the amount of additional slots aquired by items
<pre>
xslot = empire.extra_slotsl(stype)      returns int
empire.extra_slotsl(0)                  returns int / additional expedition_slots
empire.extra_slotsl(1)                  returns int / additional fleet_slots

probably a niche function, but sometimes quite useful
</pre>

### get celestial
works with planet's and moon's
<pre>
celestial = empire.celestial(id)        returns class
celestial.temperature                   returns list
celestial.diameter                      returns int
celestial.coordinates                   returns list
celestial.used                          returns int
celestial.total                         returns int
celestial.free                          returns int
celestial.points                        returns int
celestial.rank                          returns int
</pre>

### get celestial coordinates
works with planet's and moon's
<pre>
empire.celestial_coordinates(id)        returns list
</pre>

### get celestial queue
get research, building and shipyard construction time
works with planet's and moon's
<pre>
empire.celestial_queue(id, name_list)   returns list
optional input = name_list (needed for the shipyard queue)


queue = empire.celestial_queue(id)
queue.list                              returns list
queue.research                          returns datetime
queue.buildings                         returns datetime
queue.shipyard                          returns datetime
queue.squeue                            returns class / None

If ships are in queue those will now be added under squeue!

shid = queue.squeue                     returns merged class

shid.light_fighter.amount
shid.light_fighter.is_possible
shid.light_fighter.in_construction
shid.light_fighter.in_queue
shid.light_fighter.amount = shid.light_fighter.in_queue

shid.heavy_fighter
shid.cruiser
shid.battleship
shid.interceptor
shid.bomber
shid.destroyer
shid.deathstar
shid.reaper
shid.explorer
shid.small_transporter
shid.large_transporter
shid.colonyShip
shid.recycler
shid.espionage_probe
shid.solarSatellite
shid.crawler
shid.laser_cannon_light
shid.laser_cannon_heavy
shid.gauss_cannon
shid.ion_cannon
shid.plasma_cannon
shid.shield_dome_small
shid.shield_dome_large
shid.missile_interceptor
shid.missile_interplanetary


If ships are in queue and a name_list is not provided
a new file called tooltip_names.py will be created in the ogame package folder

According to your language area, a class with specific names will be added
it consists of all different ship_names followed by defence_names
</pre>

```python
class en_tooltips:
    list = [
    'Light Fighter',
    'Heavy Fighter',
    'Cruiser',
    'Battleship',
    'Battlecruiser',
    'Bomber',
    'Destroyer',
    'Deathstar',
    'Reaper',
    'Pathfinder',
    'Small Cargo',
    'Large Cargo',
    'Colony Ship',
    'Recycler',
    'Espionage Probe',
    'Solar Satellite',
    'Crawler',
    'Rocket Launcher',
    'Light Laser',
    'Heavy Laser',
    'Gauss Cannon',
    'Ion Cannon',
    'Plasma Turret',
    'Small Shield Dome',
    'Large Shield Dome',
    'Anti-Ballistic Missiles',
    'Interplanetary Missiles'
    ]
```

<pre>
If needed, those list of strings can be imported separately and used
as input for the initial empire.celestial_queue() function
-> minimizing the package import on every function call later on

just call:
empire.tooltip_names_import()           returns list
to get those names separately
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

### get/set resources settings
<pre>
empire.resources_settings(id)                       returns class(object)
empire.resources_settings(id, settings)             returns class(object)

settings = empire.resources_settings(id, settings)
settings.list                                       returns list
settings.metal_mine                                 returns int
settings.crystal_mine                               returns int
settings.deuterium_mine                             returns int
settings.solar_plant                                returns int
settings.fusion_plant                               returns int
settings.solar_satellite                            returns int
settings.crawler                                    returns int
</pre>

```python
settings = empire.resources_settings(id)

print(
       settings.list,
       settings.metal_mine,
       settings.crystal_mine,
       settings.deuterium_mine,
       settings.solar_plant,
       settings.fusion_plant,
       settings.solar_satellite,
       settings.crawler
     )

settings = empire.resources_settings(id,
        settings={
            buildings.metal_mine: speed.max,
            buildings.crystal_mine: speed.min,
            buildings.fusion_plant: 0,
            buildings.solar_satellite: speed._50,
        }
    )

print(settings.list)
```

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

sup.crystal_mine
sup.deuterium_mine
sup.solar_plant
sup.fusion_plant
sup.solar_satellite
sup.crawler
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
empire.galaxy(coordinates)                      returns list of class(object)

pos = empire.galaxy(coordinates)
pos.list                                        returns list
pos.position                                    returns list
pos.name / pos.player                           returns str
pos.rank                                        returns int
pos.status                                      returns list of str
pos.moon                                        returns bool
pos.moon_size                                   returns int / 0 if no moon
pos.alliance                                    returns str
pos.debris_coord                                return list
pos.has_debris                                  returns bool
pos.resources                                   returns list
pos.expedition_debris                           returns list  # the one for pathfinder
pos.needed_pf                                   returns int
</pre>
```python
for planet in empire.galaxy(coordinates(randint(1,6), randint(1,499))):
    print(planet.list)
    print(planet.name, planet.position, planet.player, planet.player_id, planet.rank, planet.status, planet.moon, planet.activity, planet.moon_size, planet.debris.coord, planet.has_debris, planet.resources,
planet.expedition_debris, planet.needed_pf)
    if status.inactive in planet.status and status.vacation not in planet.status:
        #Farm Inactive
```

### get debris in galaxy
<pre>
empire.galaxy_debris(coordinates)               returns list of class(object)

or use planet coordinates to get only the target debris

empire.galaxy_debris(planet_coordinates)        returns class(object)

pos = empire.galaxy_debris(planet_coordinates)
pos.list                                        returns list
pos.position                                    returns list
pos.has_debris                                  returns bool
pos.resources                                   returns list
pos.metal                                       returns int
pos.crystal                                     returns int
pos.deuterium                                   returns int
</pre>
```python
for position in empire.galaxy_debris(coordinates(1, 20)):
    print(position.list)
    print(position.position, position.has_debris, position.resources, position.metal, position.crystal, position.deuterium)
    if position.has_debris:
        # Can send recyclers

position = empire.galaxy_debris(coordinates(1, 20, 12))
print(position.list)
print(position.position, position.has_debris, position.resources, position.metal, position.crystal, position.deuterium)
if position.has_debris:
    # Can send recyclers
```

### get ally
<pre>
Returns your current Ally name None if you didnt join one yet

empire.ally()                       returns list
</pre>

### get officers
<pre>
officers = empire.officers()
officers.commander                  returns bool
officers.admiral                    returns bool
officers.engineer                   returns bool
officers.geologist                  returns bool
officers.technocrat                 returns bool
</pre>

### get shop
<pre>
empire.shop_items()                 returns list [item1, item2, ...]

The returned list consist of roughly +80 Items.
Sole purpose is to import the Item names + id.

item1 = empire.shop_items()[0]      returns list
['Researchers', '1aa36213cb676fd5baad5edc2bee4fbe117a778b']
....
....
item12 = empire.shop_items()[11]    returns list
['Bronze Crystal Booster 90d', 'bb7579f7a21152a4a256f001d5162765e2f2c5b9']

item_name = item12[0]               returns str
item_id = item12[1]                 returns str
....
first list entry resembles the item name, second one the id

empire.buy_item(id, activate_it)    return class
item = empire.buy_item(id, activate_it)
activate it set on False per default
if True the Item is bough + instant activated

name =  item.name                   return str
costs = item.costs                  return int      / DM
duration = item.duration            return duration / in s
effect = item.effect                return str      / description
amount = item.amount                return int      / used amount
list = item.list                    return list [name, costs, duration,...]

in case of failure                  return False

empire.activate_item(id)            return class
class basically the same, except another entry:
can_be_used = item.canbeused        return bool

as the function name implicates, input the item_id
and as long as enough items are in stock it will be activated
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

### jump fleet
<pre>
empire.jump_fleet(origin_id, target_id, ships)  returns bool / int (cooldown in sec)

Jumpgate is required on both moons, if there is a cooldown the function
will return the remaining seconds as an int. 
</pre>

```python
empire.jump_fleet(origin_id=id_1,
                  target_id=id_2,
                  ships=fleet(light_fighter=12, bomber=1, cruiser=100))
```

### get spyreports
<pre>
empire.spyreports()                           returns list of class(object)
empire.spyreports(firstpage=1, lastpage=30)   returns list of class(object)

reports = empire.spyreports()
report = reports[0]
report.name                                   returns str
report.position                               returns list
report.moon                                   returns bool
report.datetime                               returns str
report.metal                                  returns int
report.crystal                                returns int
report.deuterium                              returns int
report.fleet                                  returns dict
report.defenses                               returns dict
report.buildings                              returns dict
report.research                               returns dict
report.api                                    returns str
report.list                                   returns list
</pre>

```python
for report in empire.spyreports():
    print(report.list)
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

### send discovery fleet
<pre>
empire.send_fleet_discovery(coordinates(1, 2, 3))     returns string
</pre>


### send message
<pre>
empire.send_message(player_id, msg)     returns bool
</pre>

### send buddy request
<pre>
empire.send_buddy(player_id, msg)       returns bool
</pre>

### get messages
<pre>
empire.get_messages()                         returns list of class(object)

messages = empire.get_messages()
message = messages[0]
message.player                                returns str
message.player_id                             returns int
message.status  (amount of unread messages)   returns int
message.text    (text of latest message)      returns str
message.time                                  returns str
message.alliance                              returns str
message.rank                                  returns int
message.chat    (chat history of last 10 msg) returns list
message.list                                  returns list
</pre>

```python
for message in empire.get_messages():
    print(message.list)
```

### rewards
<pre>
empire.reward_system()                        returns bool (reward system online/offline)
empire.rewards()                              returns list of class(object)

items = empire.rewards() 
items.highest_tier                            returns int  (7)
items.claimable                               returns list ([1, 2, 3, 4])
items.rewards                                 returns list
items.event_progress                          returns list ([4, 7], day 4 from 7 in total)
items.list                                    returns list

example:
items.rewards  returns ([('Metal', '4.500.000', '1'), ('Crystal', '3.000.000', '2'), ('Deuterium', '1.500.000', '3')],
                        [('Commander', '4 days', '9'), ('Admiral', '4 days', '10'), ('Engineer', '4 days', '11')])


empire.rewards(tier=int, reward=int)          returns list of class(object) / bool

The desired reward level should be inserted at tier.
The reward that should be claimed at reward. (in case of three available items, 1=left, 2=middle, 3=right item)  

claimed_reward = empire.rewards(tier=int, reward=int)
if isinstance(claimed_reward, type(list)):
    claimed_reward.status                     returns bool
    claimed_reward.name                       returns str
    claimed_reward.amount                     returns str (amount of items)
    claimed_reward.id                         returns str (item id in reward system)
else:
    claimed_reward                            returns bool
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
empire.build(what=research.energy,
             id=id)

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

### deconstruct
```python
from ogame.constants import buildings
empire.deconstruct(what=buildings.metal_mine,
                   id=id)

buildings.metal_mine
buildings.crystal_mine
buildings.deuterium_mine
buildings.solar_plant
buildings.fusion_plant
buildings.metal_storage
buildings.crystal_storage
buildings.deuterium_storage

buildings.robotics_factory
buildings.shipyard
buildings.research_laboratory
buildings.missile_silo
buildings.nanite_factory

buildings.sensor_phalanx
buildings.jump_gate
```
<pre> 

                                        returns None
</pre>

### cancel building and research progress
Buildings
<pre>
If you need to cancel the construction or deconstruction of a building
empire.cancel_building(id)              returns None
</pre>
Research
<pre>
If you need to cancel the current ongoing research
empire.cancel_research(id)              returns None
</pre>

### collect rubble field
<pre> 
this will collect your rubble field at the planet id.
                
empire.collect_rubble_field(id)         returns None
</pre>

### activate/deactivate vacation mode
<pre>
empire.vacation_mode()                  returns bool / will enter vacation mode
empire.vacation_mode(activate=False)    returns bool / deactivate vacation mode

if already in vacation and the 48h arent't over yet   returns str / of time

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
