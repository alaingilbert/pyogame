class destination(object):
    planet = 1
    debris = 2
    moon = 3


def coordinates(galaxy, system, position=None, dest=destination.planet):
    return [galaxy, system, position, dest]


def convert_to_coordinates(coordinates):
    coordinates = coordinates.split('[')[1].split(']')[0].split(':')
    coordinates = [int(coordinate) for coordinate in coordinates]
    return coordinates


class mission(object):
    attack = 1
    transport = 3
    park = 4
    park_ally = 5
    spy = 6
    colonize = 7
    recycle = 8
    destroy = 9
    expedition = 15
    trade = 16


class speed(object):
    _10 = 1
    _20 = 2
    _30 = 3
    _40 = 4
    _50 = 5
    _60 = 6
    _70 = 7
    _80 = 8
    _90 = 9
    _100 = 10
    max = 10
    min = 1


class buildings(object):
    metal_mine = 1, 1, 'supplies'
    crystal_mine = 2, 1, 'supplies'
    deuterium_mine = 3, 1, 'supplies'
    solar_plant = 4, 1, 'supplies'
    fusion_plant = 12, 1, 'supplies'
    def solar_satellite(self=1): return 212, self, 'supplies'
    def crawler(self=1): return 217, self, 'supplies'
    metal_storage = 22, 1, 'supplies'
    crystal_storage = 23, 1, 'supplies'
    deuterium_storage = 24, 1, 'supplies'

    def is_supplies(supplies):
        if supplies[2] == 'supplies': return True
        else: return False

    robotics_factory = 14, 1, 'facilities'
    shipyard = 21, 1, 'facilities'
    research_laboratory = 31, 1, 'facilities'
    alliance_depot = 34, 1, 'facilities'
    missile_silo = 44, 1, 'facilities'
    nanite_factory = 15, 1, 'facilities'
    terraformer = 33, 1, 'facilities'
    repair_dock = 36, 1, 'facilities'
    moon_base = 41, 1, 'facilities'
    sensor_phalanx = 42, 1, 'facilities'
    jump_gate = 43, 1, 'facilities'

    def is_facilities(facilities):
        if facilities[2] == 'facilities': return True
        else: return False

    def rocket_launcher(self=1): return 401, self, 'defenses'
    def laser_cannon_light(self=1): return 402, self, 'defenses'
    def laser_cannon_heavy(self=1): return 403, self, 'defenses'
    def gauss_cannon(self=1): return 404, self, 'defenses'
    def ion_cannon(self=1): return 405, self, 'defenses'
    def plasma_cannon(self=1): return 406, self, 'defenses'
    def shield_dome_small(self=1): return 407, self, 'defenses'
    def shield_dome_large(self=1): return 408, self, 'defenses'
    def missile_interceptor(self=1): return 502, self, 'defenses'
    def missile_interplanetary(self=1): return 503, self, 'defenses'

    def is_defenses(defenses):
        if defenses[2] == 'defenses': return True
        else: return False


class research(object):
    energy = 113, 1, 'research'
    laser = 120, 1, 'research'
    ion = 121, 1, 'research'
    hyperspace = 114, 1, 'research'
    plasma = 122, 1, 'research'
    combustion_drive = 115, 1, 'research'
    impulse_drive = 117, 1, 'research'
    hyperspace_drive = 118, 1, 'research'
    espionage = 106, 1, 'research'
    computer = 108, 1, 'research'
    astrophysics = 124, 1, 'research'
    research_network = 123, 1, 'research'
    graviton = 199, 1, 'research'
    weapons = 109, 1, 'research'
    shielding = 110, 1, 'research'
    armor = 111, 1, 'research'


class ships(object):
    def light_fighter(self=1): return 204, self, 'shipyard'
    def heavy_fighter(self=1): return 205, self, 'shipyard'
    def cruiser(self=1): return 206, self, 'shipyard'
    def battleship(self=1): return 207, self, 'shipyard'
    def interceptor(self=1): return 215, self, 'shipyard'
    def bomber(self=1): return 211, self, 'shipyard'
    def destroyer(self=1): return 213, self, 'shipyard'
    def deathstar(self=1): return 214, self, 'shipyard'
    def reaper(self=1): return 218, self, 'shipyard'
    def explorer(self=1): return 219, self, 'shipyard'
    def small_transporter(self=1): return 202, self, 'shipyard'
    def large_transporter(self=1): return 203, self, 'shipyard'
    def colonyShip(self=1): return 208, self, 'shipyard'
    def recycler(self=1): return 209, self, 'shipyard'
    def espionage_probe(self=1): return 210, self, 'shipyard'

    def is_ship(ship):
        if ship[2] == 'shipyard':
            return True
        else:
            return False

    def ship_name(ship):
        if ships.is_ship(ship):
            if ship[0] == 204: return 'light_fighter'
            elif ship[0] == 205: return 'heavy_fighter'
            elif ship[0] == 206: return 'cruiser'
            elif ship[0] == 207: return 'battleship'
            elif ship[0] == 215: return 'interceptor'
            elif ship[0] == 211: return 'bomber'
            elif ship[0] == 213: return 'destroyer'
            elif ship[0] == 214: return 'deathstar'
            elif ship[0] == 218: return 'reaper'
            elif ship[0] == 219: return 'explorer'
            elif ship[0] == 202: return 'small_transporter'
            elif ship[0] == 203: return 'large_transporter'
            elif ship[0] == 208: return 'colonyShip'
            elif ship[0] == 209: return 'recycler'
            elif ship[0] == 210: return 'espionage_probe'
            elif ship[0] == 217: return 'crawler'

    def ship_amount(ship):
        if ships.is_ship(ship):
            return ship[1]

    def ship_id(ship):
        if ships.is_ship(ship):
            return ship[0]


def convert_tech(code, category):
    return code, 1, category


def resources(metal=0.0, crystal=0.0, deuterium=0.0):
    return [int(metal), int(crystal), int(deuterium)]


class status:
    active = 'active'
    inactive = 'inactive'
    vacation = 'vacation'
    noob = 'newbie'
    honorableTarget = 'strong'
    online = 'online'
    recently = 'recently'
    offline = 'offline'


class messages:
    spy_reports = 20


def price(technology, level=1):
    def multipli_resources(resources, multiplyer):
        return [resource*multiplyer for resource in resources]

    if ships.is_ship(technology):
        if technology[0] == 204: return multipli_resources([3000, 1000, 0], technology[1])
        elif technology[0] == 205: return multipli_resources([6000, 4000, 0], technology[1])
        elif technology[0] == 206: return multipli_resources([20000, 7000, 2000], technology[1])
        elif technology[0] == 207: return multipli_resources([45000, 15000, 0], technology[1])
        elif technology[0] == 215: return multipli_resources([30000, 40000, 15000], technology[1])
        elif technology[0] == 211: return multipli_resources([50000, 25000, 15000], technology[1])
        elif technology[0] == 213: return multipli_resources([60000, 50000, 15000], technology[1])
        elif technology[0] == 214: return multipli_resources([5000000, 4000000, 1000000], technology[1])
        elif technology[0] == 218: return multipli_resources([85000, 55000, 20000], technology[1])
        elif technology[0] == 219: return multipli_resources([8000, 15000, 8000], technology[1])
        elif technology[0] == 202: return multipli_resources([2000, 2000, 0], technology[1])
        elif technology[0] == 203: return multipli_resources([6000, 6000, 0], technology[1])
        elif technology[0] == 208: return multipli_resources([10000, 20000, 10000], technology[1])
        elif technology[0] == 209: return multipli_resources([10000, 6000, 2000], technology[1])
        elif technology[0] == 210: return multipli_resources([0, 1000, 0], technology[1])
        elif technology[0] == 217: return multipli_resources([2000, 2000, 1000], technology[1])

    if buildings.is_supplies(technology):
        if technology[0] == 1: return resources(metal=60 * 1.5 ** level, crystal=15 * 1.5 ** level)
        elif technology[0] == 2: return resources(metal=48 * 1.6 ** level, crystal=24 * 1.6 ** level)
        elif technology[0] == 3: return resources(metal=225 * 1.5 ** level, crystal=75 * 1.5 ** level)
        elif technology[0] == 4: return resources(metal=75 * 1.5 ** level, crystal=30 * 1.5 ** level)
        elif technology[0] == 12: return resources(900 * 1.8 ** level, 360 * 1.8 ** level, 180 * 1.8 ** level)
        elif technology[0] == 22: return resources(metal=1000 * 2 ** level)
        elif technology[0] == 23: return resources(metal=1000 * 2 ** level, crystal=500 * 2 ** level)
        elif technology[0] == 24: return resources(metal=1000 * 2 ** level, crystal=1000 * 2 ** level)
        elif technology[0] == 212: return multipli_resources([0, 2000, 500], technology[1])
        elif technology[0] == 217: return multipli_resources([2000, 2000, 1000], technology[1])

    if buildings.is_facilities(technology):
        if technology[0] == 14: return resources(400 * 2 ** level, 120 * 2 ** level, 200 * 2 ** level)
        elif technology[0] == 21: return resources(200 * 2 ** level, 100 * 2 ** level, 50 * 2 ** level)
        elif technology[0] == 31: return resources(200 * 2 ** level, 400 * 2 ** level, 200 * 2 ** level)
        elif technology[0] == 34: return resources(metal=10000 * 2 ** level, crystal=20000 * 2 ** level)
        elif technology[0] == 44: return resources(20000 * 2 ** level, 20000 * 2 ** level, 1000 * 2 ** level)
        elif technology[0] == 15: return resources(1000000 * 2 ** level, 500000 * 2 ** level, 100000 * 2 ** level)
        elif technology[0] == 33: return resources(crystal=50000 * 2 ** level, deuterium=100000 * 2 ** level)
        elif technology[0] == 36: return resources(metal=40 * 5 ** level, deuterium=10 * 5 ** level)
        elif technology[0] == 41: return resources(10000 * 2 ** level, 20000 * 2 ** level, 10000 * 2 ** level)
        elif technology[0] == 42: return resources(10000 * 2 ** level, 20000 * 2 ** level, 10000 * 2 ** level)
        elif technology[0] == 43: return resources(10000 * 2 ** level, 20000 * 2 ** level, 10000 * 2 ** level)

    if buildings.is_defenses(technology):
        if technology[0] == 401: return multipli_resources([2000, 0, 0], technology[1])
        elif technology[0] == 402: return multipli_resources([1500, 500, 0], technology[1])
        elif technology[0] == 403: return multipli_resources([6000, 2000, 0], technology[1])
        elif technology[0] == 404: return multipli_resources([20000, 15000, 2000], technology[1])
        elif technology[0] == 405: return multipli_resources([5000, 3000, 0], technology[1])
        elif technology[0] == 406: return multipli_resources([50000, 50000, 30000], technology[1])
        elif technology[0] == 407: return multipli_resources([10000, 10000, 0], technology[1])
        elif technology[0] == 408: return multipli_resources([50000, 50000, 0], technology[1])
        elif technology[0] == 502: return multipli_resources([8000, 2000, 0], technology[1])
        elif technology[0] == 503: return multipli_resources([12500, 2500, 10000], technology[1])
