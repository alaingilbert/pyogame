from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID, NOT_LOGGED, BAD_CREDENTIALS
from bs4 import BeautifulSoup
from dateutil import tz

import arrow
import datetime
import requests
import json
import math
import re


def parse_int(text):
    return int(text.replace('.', '').strip())


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def sandbox(some_fn):
    def wrapper(ogame, *args, **kwargs):
        fn_name = some_fn.__name__

        if fn_name == '__init__' or not ogame.sandbox:
            return some_fn(ogame, *args, **kwargs)

        if fn_name in ogame.sandbox_obj:
            return ogame.sandbox_obj[fn_name]

        res = None
        if fn_name == 'login':
            res = None
        elif fn_name == 'get_resources':
            res = {'metal': 0, 'crystal': 0, 'deuterium': 0, 'energy': 0, 'darkmatter': 0}
        elif fn_name == 'get_universe_speed':
            res = 1
        elif fn_name == 'get_user_infos':
            res = {}
            res['player_id'] = 0
            res['player_name'] = 'Sandbox'
            res['points'] = 0
            res['rank'] = 0
            res['total'] = 0
            res['honour_points'] = 0
            res['planet_ids'] = []

        return res
    return wrapper


@for_all_methods(sandbox)
class OGame(object):
    def __init__(self, universe, username, password, domain='en.ogame.gameforge.com', auto_bootstrap=True, sandbox=False, sandbox_obj={}):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})
        self.sandbox = sandbox
        self.sandbox_obj = sandbox_obj
        self.universe = universe
        self.domain = domain
        self.username = username
        self.password = password
        self.universe_speed = 1
        self.server_url = ''
        self.server_tz = 'GMT+1'
        if auto_bootstrap:
            self.login()
            self.universe_speed = self.get_universe_speed()

    def login(self):
        """Get the ogame session token."""
        if self.server_url == '':
            self.server_url = self.get_universe_url(self.universe)
        payload = {'kid': '',
                   'uni': self.server_url,
                   'login': self.username,
                   'pass': self.password}
        res = self.session.post(self.get_url('login'), data=payload).content
        soup = BeautifulSoup(res)
        session_found = soup.find('meta', {'name': 'ogame-session'})
        if session_found:
            self.ogame_session = session_found.get('content')
        else:
            raise BAD_CREDENTIALS

    def logout(self):
        self.session.get(self.get_url('logout'))

    def is_logged(self):
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res)
        session = soup.find('meta', {'name': 'ogame-session'})
        return session is not None

    def get_page_content(self, page='overview'):
        """Return the html of a specific page."""
        return self.session.get(self.get_url(page)).content

    def fetch_eventbox(self):
        res = self.session.get(self.get_url('fetchEventbox')).content
        try:
            obj = json.loads(res)
        except ValueError, e:
            raise NOT_LOGGED
        return obj

    def fetch_resources(self, planet_id):
        url = self.get_url('fetchResources', {'cp': planet_id})
        res = self.session.get(url).content
        try:
            obj = json.loads(res)
        except ValueError, e:
            raise NOT_LOGGED
        return obj

    def get_resources(self, planet_id):
        """Returns the planet resources stats."""
        resources = self.fetch_resources(planet_id)
        metal = resources['metal']['resources']['actual']
        crystal = resources['crystal']['resources']['actual']
        deuterium = resources['deuterium']['resources']['actual']
        energy = resources['energy']['resources']['actual']
        darkmatter = resources['darkmatter']['resources']['actual']
        result = {'metal': metal, 'crystal': crystal, 'deuterium': deuterium,
                  'energy': energy, 'darkmatter': darkmatter}
        return result

    def get_universe_speed(self):
        res = self.session.get(self.get_url('techtree', {'tab': 2, 'techID': 1})).content
        soup = BeautifulSoup(res)
        tr = soup.find('tr', {'class': 'detailTableRow'})
        spans = soup.findAll('span', {'class': 'undermark'})
        level = parse_int(spans[0].text)
        val = parse_int(spans[1].text)
        metal_production = self.metal_mine_production(level, 1)
        universe_speed = val / metal_production
        return universe_speed

    def metal_mine_production(self, level, universe_speed=1):
        return int(math.floor(30 * level * 1.1 ** level) * universe_speed)

    def crystal_mine_production(level, universe_speed=1):
        return int(math.floor(20 * level * 1.1 ** level) * universe_speed)

    def deuterium_synthesizer_production(level, max_temperature, universe_speed=1):
        return int(math.floor(10 * level * 1.1 ** level) * (1.44 - 0.004 * max_temperature) * universe_speed)

    def SolarPlantProduction(level):
        return int(math.floor(20 * level * 1.1 ** level))

    def metal_mine_cost(level):
        metal = int(60 * 1.5 ** (level-1))
        crystal = int(15 * 1.5 ** (level-1))
        return (metal, crystal)

    def crystal_mine_cost(level):
        metal = int(48 * 1.6 ** (level-1))
        crystal = int(24 * 1.6 ** (level-1))
        return (metal, crystal)

    def deuterium_synthesizer_cost(level):
        metal = int(225 * 1.5 ** (level-1))
        crystal = int(75 * 1.5 ** (level-1))
        return (metal, crystal)

    def solar_plant_cost(level):
        metal = int(75 * 1.5 ** (level-1))
        crystal = int(30 * 1.5 ** (level-1))
        return (metal, crystal)

    def fusion_reactor_cost(level):
        metal = int(900 * 1.8 ** (level-1))
        crystal = int(360 * 1.8 ** (level-1))
        deuterium = int(180 * 1.8 ** (level-1))
        return (metal, crystal, deuterium)

    def building_production_time(metal, crystal, level_robotics_factory, level_nanite_factory, level, universe_speed=1):
        res = (metal + crystal) / (2500 * max(4-level/2, 1) * (1 + level_robotics_factory) * universe_speed * 2 ** level_nanite_factory) * 3600
        seconds = int(round(res))
        return seconds

    def building_production_time2(metal, crystal, level_robotics_factory, level_nanite_factory, level, universe_speed=1):
        """Nanite Factories, Lunar Bases, Sensor Phalanxes, and Jumpgates do not get the MAX() time reduction, so their formula is just"""
        res = (metal + crystal) / (2500 * (1 + level_robotics_factory) * universe_speed * 2 ** level_nanite_factory) * 3600
        seconds = int(round(res))
        return seconds

    def research_time(metal, crystal, research_lab_level):
        res = (metal + crystal) / (1000 * (1 + research_lab_level))
        seconds = int(round(res))
        return seconds

    def ships_defense_time(metal, crystal, shipyard_level, nanite_factory_level):
        res = (metal + crystal) / (2500 * (1 + shipyard_level) * (2 ^ nanite_factory_level))
        seconds = int(round(res))
        return seconds

    def get_user_infos(self):
        html = self.session.get(self.get_url('overview')).content
        res = {}
        res['player_id'] = int(re.search(r'playerId="(\w+)"', html).group(1))
        res['player_name'] = re.search(r'playerName="(\w+)"', html).group(1)
        tmp = re.search(r'textContent\[7\]="([^"]+)"', html).group(1)
        soup = BeautifulSoup(tmp)
        tmp = soup.text
        infos = re.search(r'([\d\\.]+) \(Place ([\d\.]+) of ([\d\.]+)\)', tmp)
        res['points'] = parse_int(infos.group(1))
        res['rank'] = parse_int(infos.group(2))
        res['total'] = parse_int(infos.group(3))
        res['honour_points'] = parse_int(re.search(r'textContent\[9\]="([^"]+)"', html).group(1))
        res['planet_ids'] = self.get_planet_ids(html)
        return res

    def get_nbr(self, soup, name):
        div = soup.find('div', {'class': name})
        level = div.find('span', {'class': 'level'})
        for tag in level.findAll(True):
            tag.extract()
        return parse_int(level.text)

    def get_resources_buildings(self, planet_id):
        res = self.session.get(self.get_url('resources')).content
        soup = BeautifulSoup(res)
        res = {}
        res['metal_mine'] = self.get_nbr(soup, 'supply1')
        res['crystal_mine'] = self.get_nbr(soup, 'supply2')
        res['deuterium_synthesizer'] = self.get_nbr(soup, 'supply3')
        res['solar_plant'] = self.get_nbr(soup, 'supply4')
        res['fusion_reactor'] = self.get_nbr(soup, 'supply12')
        res['solar_satellite'] = self.get_nbr(soup, 'supply212')
        res['metal_storage'] = self.get_nbr(soup, 'supply22')
        res['crystal_storage'] = self.get_nbr(soup, 'supply23')
        res['deuterium_tank'] = self.get_nbr(soup, 'supply24')
        return res

    def get_defense(self, planet_id):
        res = self.session.get(self.get_url('defense')).content
        soup = BeautifulSoup(res)
        res = {}
        res['rocket_launcher'] = self.get_nbr(soup, 'defense401')
        res['light_laser'] = self.get_nbr(soup, 'defense402')
        res['heavy_laser'] = self.get_nbr(soup, 'defense403')
        res['gauss_cannon'] = self.get_nbr(soup, 'defense404')
        res['ion_cannon'] = self.get_nbr(soup, 'defense405')
        res['plasma_turret'] = self.get_nbr(soup, 'defense406')
        res['small_shield_dome'] = self.get_nbr(soup, 'defense407')
        res['large_shield_dome'] = self.get_nbr(soup, 'defense408')
        res['anti_ballistic_missiles'] = self.get_nbr(soup, 'defense502')
        res['interplanetary_missiles'] = self.get_nbr(soup, 'defense503')
        return res

    def get_ships(self, planet_id):
        res = self.session.get(self.get_url('shipyard', {'cp': planet_id})).content
        soup = BeautifulSoup(res)
        res = {}
        res['light_fighter'] = self.get_nbr(soup, 'military204')
        res['heavy_fighter'] = self.get_nbr(soup, 'military205')
        res['cruiser'] = self.get_nbr(soup, 'military206')
        res['battleship'] = self.get_nbr(soup, 'military207')
        res['battlecruiser'] = self.get_nbr(soup, 'military215')
        res['bomber'] = self.get_nbr(soup, 'military211')
        res['destroyer'] = self.get_nbr(soup, 'military213')
        res['deathstar'] = self.get_nbr(soup, 'military214')
        res['small_cargo'] = self.get_nbr(soup, 'civil202')
        res['large_cargo'] = self.get_nbr(soup, 'civil203')
        res['colony_ship'] = self.get_nbr(soup, 'civil208')
        res['recycler'] = self.get_nbr(soup, 'civil209')
        res['espionage_probe'] = self.get_nbr(soup, 'civil210')
        res['solar_satellite'] = self.get_nbr(soup, 'civil212')
        return res

    def get_facilities(self, planet_id):
        res = self.session.get(self.get_url('station', {'cp': planet_id})).content
        soup = BeautifulSoup(res)
        res = {}
        res['robotics_factory'] = self.get_nbr(soup, 'station14')
        res['shipyard'] = self.get_nbr(soup, 'station21')
        res['research_lab'] = self.get_nbr(soup, 'station31')
        res['alliance_depot'] = self.get_nbr(soup, 'station34')
        res['missile_silo'] = self.get_nbr(soup, 'station44')
        res['nanite_factory'] = self.get_nbr(soup, 'station15')
        res['terraformer'] = self.get_nbr(soup, 'station33')
        res['space_dock'] = self.get_nbr(soup, 'station36')
        return res

    def get_research(self):
        res = self.session.get(self.get_url('research')).content
        soup = BeautifulSoup(res)
        res = {}
        res['energy_technology'] = self.get_nbr(soup, 'research113')
        res['laser_technology'] = self.get_nbr(soup, 'research120')
        res['ion_technology'] = self.get_nbr(soup, 'research121')
        res['hyperspace_technology'] = self.get_nbr(soup, 'research114')
        res['plasma_technology'] = self.get_nbr(soup, 'research122')
        res['combustion_drive'] = self.get_nbr(soup, 'research115')
        res['impulse_drive'] = self.get_nbr(soup, 'research117')
        res['hyperspace_drive'] = self.get_nbr(soup, 'research118')
        res['espionage_technology'] = self.get_nbr(soup, 'research106')
        res['computer_technology'] = self.get_nbr(soup, 'research108')
        res['astrophysics'] = self.get_nbr(soup, 'research124')
        res['intergalactic_research_network'] = self.get_nbr(soup, 'research123')
        res['graviton_technology'] = self.get_nbr(soup, 'research199')
        res['weapons_technology'] = self.get_nbr(soup, 'research109')
        res['shielding_technology'] = self.get_nbr(soup, 'research110')
        res['armour_technology'] = self.get_nbr(soup, 'research111')
        return res

    def is_under_attack(self):
        json = self.fetch_eventbox()
        return not json.get('hostile', 0) == 0

    def get_planet_ids(self, res=None):
        """Get the ids of your planets."""
        if not res:
            res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res)
        planets = soup.findAll('div', {'class': 'smallplanet'})
        ids = [planet['id'].replace('planet-', '') for planet in planets]
        return ids

    def get_planet_by_name(self, planet_name):
        """Returns the first planet id with the specified name."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res)
        planets = soup.findAll('div', {'class': 'smallplanet'})
        for planet in planets:
            name = planet.find('span', {'class': 'planet-name'}).string
            if name == planet_name:
                id = planet['id'].replace('planet-', '')
                return id
        return None

    def build_defense(self, planet_id, defense_id, nbr):
        """Build a defense unit."""
        if defense_id not in constants.Defense.values():
            raise BAD_DEFENSE_ID

        url = self.get_url('defense', {'cp': planet_id})

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': defense_id}
        self.session.post(url, data=payload)

    def build_ships(self, planet_id, ship_id, nbr):
        """Build a ship unit."""
        if ship_id not in constants.Ships.values():
            raise BAD_SHIP_ID

        url = self.get_url('shipyard', {'cp': planet_id})

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': ship_id}
        self.session.post(url, data=payload)

    def build_building(self, planet_id, building_id):
        """Build a ship unit."""
        if building_id not in constants.Buildings.values():
            raise BAD_BUILDING_ID

        url = self.get_url('resources', {'cp': planet_id})

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        #is_idle = bool(soup.find('td', {'class': 'idle'}))
        #if not is_idle:
        #    return False
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'modus': 1,
                   'token': token,
                   'type': building_id}
        self.session.post(url, data=payload)
        #return True

    def build_technology(self, planet_id, technology_id):
        if technology_id not in constants.Research.values():
            raise BAD_RESEARCH_ID

        url = self.get_url('research', {'cp': planet_id})

        payload = {'modus': 1,
                   'type': technology_id}
        self.session.post(url, data=payload)

    def _build(self, planet_id, object_id, nbr=None):
        if object_id in constants.Buildings.values():
            self.build_building(planet_id, object_id)
        elif object_id in constants.Research.values():
            self.build_technology(planet_id, object_id)
        elif object_id in constants.Ships.values():
            self.build_ships(planet_id, object_id, nbr)
        elif object_id in constants.Defense.values():
            self.build_defense(planet_id, object_id, nbr)

    def build(self, planet_id, arg):
        if isinstance(arg, list):
            for el in arg:
                self.build(planet_id, el)
        elif isinstance(arg, tuple):
            elem_id, nbr = arg
            self._build(planet_id, elem_id, nbr)
        else:
            elem_id = arg
            self._build(planet_id, elem_id)

    def send_fleet(self, planet_id, ships, speed, where, mission, resources):
        def get_hidden_fields(html):
            soup = BeautifulSoup(html)
            inputs = soup.findAll('input', {'type': 'hidden'})
            fields = {}
            for input in inputs:
                name = input.get('name')
                value = input.get('value')
                fields[name] = value
            return fields

        url = self.get_url('fleet1', {'cp': planet_id})

        res = self.session.get(url).content
        payload = {}
        payload.update(get_hidden_fields(res))
        for name, value in ships:
            payload['am%s' % name] = value
        res = self.session.post(self.get_url('fleet2'), data=payload).content

        payload = {}
        payload.update(get_hidden_fields(res))
        payload.update({'speed': speed,
                        'galaxy': where.get('galaxy'),
                        'system': where.get('system'),
                        'position': where.get('position')})
        res = self.session.post(self.get_url('fleet3'), data=payload).content

        payload = {}
        payload.update(get_hidden_fields(res))
        payload.update({'crystal': resources.get('crystal'),
                        'deuterium': resources.get('deuterium'),
                        'metal': resources.get('metal'),
                        'mission': mission})
        res = self.session.post(self.get_url('movement'), data=payload).content

        res = self.session.get(self.get_url('movement')).content
        soup = BeautifulSoup(res)
        origin_coords = soup.find('meta', {'name': 'ogame-planet-coordinates'})['content']
        fleets = soup.findAll('div', {'class': 'fleetDetails'})
        for fleet in fleets:
            origin = fleet.find('span', {'class': 'originCoords'}).text
            dest = fleet.find('span', {'class': 'destinationCoords'}).text
            fleet_id = int(fleet.find('span', {'class': 'reversal'}).get('ref'))
            if dest == '[%s:%s:%s]' % (where['galaxy'], where['system'], where['position']) and origin == '[%s]' % origin_coords:
                return fleet_id

    def cancel_fleet(self, fleet_id):
        self.session.get(self.get_url('movement') + '&return=%s' % fleet_id)

    def get_fleet_ids(self):
        """Return the reversable fleet ids."""
        res = self.session.get(self.get_url('movement')).content
        soup = BeautifulSoup(res)
        spans = soup.findAll('span', {'class': 'reversal'})
        fleet_ids = [span.get('ref') for span in spans]
        return fleet_ids

    def get_attacks(self):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(self.get_url('eventList'), params={'ajax': 1},
                               headers=headers).content
        soup = BeautifulSoup(res)
        events = soup.findAll('tr', {'class': 'eventFleet'})
        attacks = []
        for ev in events:
            mission_type = int(ev['data-mission-type'])
            if mission_type != 1:
                continue

            attack = {}
            coords_origin = ev.find('td', {'class': 'coordsOrigin'}) \
                              .text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_origin)
            galaxy, system, position = coords.groups()
            attack.update({'origin': (int(galaxy), int(system), int(position))})

            dest_coords = ev.find('td', {'class': 'destCoords'}).text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', dest_coords)
            galaxy, system, position = coords.groups()
            attack.update({'destination': (int(galaxy), int(system), int(position))})

            arrival_time = ev.find('td', {'class': 'arrivalTime'}).text.strip()
            coords = re.search(r'(\d+):(\d+):(\d+)', arrival_time)
            hour, minute, second = coords.groups()
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            arrival_time = self.get_datetime_from_time(hour, minute, second)
            attack.update({'arrival_time': arrival_time})

            attacker_id = ev.find('a', {'class': 'sendMail'})['data-playerid']
            attack.update({'attacker_id': int(attacker_id)})

            attacks.append(attack)
        return attacks

    def get_datetime_from_time(self, hour, minute, second):
        attack_time = arrow.utcnow().to(self.server_tz).replace(hour=hour, minute=minute, second=second)
        now = arrow.utcnow().to(self.server_tz)
        if now.hour > attack_time.hour:
            attack_time += datetime.timedelta(days=1)
        return attack_time.to(tz.tzlocal()).datetime

    def get_url(self, page, params={}):
        if page == 'login':
            return 'https://%s/main/login' % self.domain
        else:
            if self.server_url == '':
                self.server_url = self.get_universe_url(universe)
            url = 'https://%s/game/index.php?page=%s' % (self.server_url, page)
            if params:
                arr = []
                for key in params:
                    arr.append("%s=%s" % (key, params[key]))
                url += '&' + '&'.join(arr)
            return url

    def get_servers(self, domain):
        res = self.session.get('https://%s' % domain).content
        soup = BeautifulSoup(res)
        select = soup.find('select', {'id': 'serverLogin'})
        servers = {}
        for opt in select.findAll('option'):
            url = opt.get('value')
            name = opt.string.strip().lower()
            servers[name] = url
        return servers

    def get_universe_url(self, universe):
        """Get a universe name and return the server url."""
        servers = self.get_servers(self.domain)
        universe = universe.lower()
        if universe not in servers:
            raise BAD_UNIVERSE_NAME
        return servers[universe]

    def get_server_time(self):
        """Get the ogame server time."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res)
        date_str = soup.find('li', {'class': 'OGameClock'}).text
        format = '%d.%m.%Y %H:%M:%S'
        date = datetime.datetime.strptime(date_str, format)
        return date

    def get_planet_infos_regex(self, text):
        return re.search(r'(\w+) \[(\d+):(\d+):(\d+)\]([\d\.]+)km \((\d+)/(\d+)\)([-\d]+).+C (?:bis|to) ([-\d]+).+C', text)

    def get_planet_infos(self, planet_id):
        res = self.session.get(self.get_url('overview', {'cp': planet_id})).content
        soup = BeautifulSoup(res)
        link = soup.find('div', {'id': 'planet-%s' % planet_id}).find('a')
        infos_label = BeautifulSoup(link['title']).text
        infos = self.get_planet_infos_regex(infos_label)
        res = {}
        res['img'] = link.find('img').get('src')
        res['id'] = planet_id
        res['planet_name'] = infos.group(1)
        res['coordinate'] = {}
        res['coordinate']['galaxy'] = int(infos.group(2))
        res['coordinate']['system'] = int(infos.group(3))
        res['coordinate']['position'] = int(infos.group(4))
        res['diameter'] = parse_int(infos.group(5))
        res['fields'] = {}
        res['fields']['built'] = int(infos.group(6))
        res['fields']['total'] = int(infos.group(7))
        res['temperature'] = {}
        res['temperature']['min'] = int(infos.group(8))
        res['temperature']['max'] = int(infos.group(9))
        return res

    def get_ogame_version(self):
        """Get ogame version on your server."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res)
        footer = soup.find('div', {'id': 'siteFooter'})
        version = footer.find('a').text.strip()
        return version

    def get_code(self, name):
        if name in constants.Buildings.keys():
            return constants.Buildings[name]
        if name in constants.Facilities.keys():
            return constants.Facilities[name]
        if name in constants.Defense.keys():
            return constants.Defense[name]
        if name in constants.Ships.keys():
            return constants.Ships[name]
        if name in constants.Research.keys():
            return constants.Research[name]
        print 'Couldn\'t find code for %s' % name
        return None

    def get_overview(self, planet_id):
        html = self.session.get(self.get_url('overview', {'cp': planet_id})).content
        soup = BeautifulSoup(html)
        boxes = soup.findAll('div', {'class': 'content-box-s'})
        res = {}
        names = ['buildings', 'research', 'shipyard']
        for idx, box in enumerate(boxes):
            isIdle = box.find('td', {'class': 'idle'}) is not None
            res[names[idx]] = None
            if not isIdle:
                name = box.find('th').text
                short_name = ''.join(name.split())
                code = self.get_code(short_name)
                desc = box.find('td', {'class': 'desc'}).text
                desc = ' '.join(desc.split())
                tmp = {'name': short_name, 'code': code}
                if idx == 2:
                    quantity = parse_int(box.find('div', {'id': 'shipSumCount7'}).text)
                    tmp.update({'quantity': quantity})
                    tmp = [tmp]
                    queue = box.find('table', {'class': 'queue'})
                    if queue:
                        tds = queue.findAll('td')
                        for td in tds:
                            link = td.find('a')
                            quantity = parse_int(link.text)
                            img = td.find('img')
                            alt = img['alt']
                            short_name = ''.join(alt.split())
                            code = self.get_code(short_name)
                            tmp.append({'name': short_name, 'code': code, 'quantity': quantity})
                res[names[idx]] = tmp
        return res

    def get_resource_settings(self, planet_id):
        html = self.session.get(self.get_url('resourceSettings', {'cp': planet_id})).content
        soup = BeautifulSoup(html)
        options = soup.find_all('option', {'selected': True})
        res = {}
        res['metal_mine']            = options[0]['value']
        res['crystal_mine']          = options[1]['value']
        res['deuterium_synthesizer'] = options[2]['value']
        res['solar_plant']           = options[3]['value']
        res['fusion_reactor']        = options[4]['value']
        res['solar_satellite']       = options[5]['value']
        return res

    def send_message(self, player_id, msg):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        payload = {'playerId': player_id,
                   'text': msg,
                   'mode': 1,
                   'ajax': 1}
        url = self.get_url('ajaxChat')
        self.session.post(url, data=payload, headers=headers)
