from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID, NOT_LOGGED
from bs4 import BeautifulSoup

import datetime
import requests
import json
import math
import re


class OGame(object):
    def __init__(self, universe, username, password, domain='en.ogame.gameforge.com', auto_bootstrap=True):
        self.session = requests.session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})
        self.universe = universe
        self.domain = domain
        self.username = username
        self.password = password
        self.universe_speed = 1
        self.server_url = ''
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
                   'pass': self.password,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'}                   
        res = self.session.post(self.get_url('login'), data=payload).content
        soup = BeautifulSoup(res, "lxml")
        self.ogame_session = soup.find('meta', {'name': 'ogame-session'}) \
                                 .get('content')

    def logout(self):
        self.session.get(self.get_url('logout'))

    def is_logged(self):
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
        tr = soup.find('tr', {'class': 'detailTableRow'})
        spans = soup.findAll('span', {'class': 'undermark'})
        level = int(spans[0].text.strip())
        val = int(spans[1].text.replace('.', '').strip())
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
        if "de.ogame" in self.domain:
            infos = re.search(r'([\d\\.]+) \(Platz ([\d\.]+) von ([\d\.]+)\)', tmp)
        else:
            infos = re.search(r'([\d\\.]+) \(Place ([\d\.]+) of ([\d\.]+)\)', tmp)      
        res['points'] = int(infos.group(1).replace('.', ''))
        res['rank'] = int(infos.group(2).replace('.', ''))
        res['total'] = int(infos.group(3).replace('.', ''))
        res['honour_points'] = int(re.search(r'textContent\[9\]="([^"]+)"', html).group(1).replace('.', ''))
        return res

    def get_nbr(self, soup, name):
        div = soup.find('div', {'class': name})
        level = div.find('span', {'class': 'level'})
        for tag in level.findAll(True):
            tag.extract()
        return int(level.text.strip())

    def get_resources_buildings(self, planet_id):
        res = self.session.get(self.get_url('resources')).content
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
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
        res = self.session.get(self.get_url('shipyard')).content
        soup = BeautifulSoup(res, "lxml")
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

    def get_facilities(self):
        res = self.session.get(self.get_url('station')).content
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
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

    def get_planet_ids(self):
        """Get the ids of your planets."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res, "lxml")
        planets = soup.findAll('div', {'class': 'smallplanet'})
        ids = [planet['id'].replace('planet-', '') for planet in planets]
        return ids

    def get_planet_by_name(self, planet_name):
        """Returns the first planet id with the specified name."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': ship_id}
        self.session.post(url, data=payload)

    def build_building(self, planet_id, building_id):
        """Build a building."""
        if building_id not in constants.Buildings.values():
            raise BAD_BUILDING_ID

        url = self.get_url('resources', {'cp': planet_id})

        res = self.session.get(url).content
        soup = BeautifulSoup(res, "lxml")
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'modus': 1,
                   'token': token,
                   'type': building_id}
        self.session.post(url, data=payload)

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
        # TODO: Should return the fleet ID.

    def cancel_fleet(self, fleet_id):
        self.session.get(self.get_url('movement') + '&return=%s' % fleet_id)

    def get_fleet_ids(self):
        """Return the reversable fleet ids."""
        res = self.session.get(self.get_url('movement')).content
        soup = BeautifulSoup(res, "lxml")
        spans = soup.findAll('span', {'class': 'reversal'})
        fleet_ids = [span.get('ref') for span in spans]
        return fleet_ids

    def get_attacks(self):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(self.get_url('eventList'), params={'ajax': 1},
                               headers=headers).content
        soup = BeautifulSoup(res, "lxml")
        events = soup.findAll('tr', {'class': 'eventFleet'})
        attacks = []
        for ev in events:
            attack = {}
            coords_origin = ev.find('td', {'class': 'coordsOrigin'}) \
                              .text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_origin)
            galaxy, system, position = coords.groups()
            attack.update({'origin': (galaxy, system, position)})

            dest_coords = ev.find('td', {'class': 'destCoords'}).text.strip()
            coords = re.search(r'\[(\d+):(\d+):(\d+)\]', coords_origin)
            galaxy, system, position = coords.groups()
            attack.update({'destination': (galaxy, system, position)})

            arrival_time = ev.find('td', {'class': 'arrivalTime'}).text.strip()
            coords = re.search(r'(\d+):(\d+):(\d+)', arrival_time)
            hour, minute, second = coords.groups()
            arrival_time = get_datetime_from_time(hour, minute, second)
            attack.update({'arrival_time': arrival_time})

            attacks.append(attack)
        return attacks

    def get_datetime_from_time(self, hour, minute, second):
        now = datetime.datetime.now()
        current_hour = now.hour
        date = datetime.date.today()
        if hour < current_hour:
            date += datetime.timedelta(days=1)
        time = datetime.time(hour, minute, second)
        arrival_time = datetime.datetime.combine(date, time)
        return arrival_time

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
        soup = BeautifulSoup(res, "lxml")
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
        soup = BeautifulSoup(res, "lxml")
        date_str = soup.find('li', {'class': 'OGameClock'}).text
        format = '%d.%m.%Y %H:%M:%S'
        date = datetime.datetime.strptime(date_str, format)
        return date

    def get_planet_infos(self, planet_id):
        res = self.session.get(self.get_url('overview', {'cp': planet_id})).content
        soup = BeautifulSoup(res, "lxml")
        link = soup.find('div', {'id': 'planet-%s' % planet_id}).find('a')
        infos_label = BeautifulSoup(link['title']).text
        infos = re.search(r'(\w+) \[(\d+):(\d+):(\d+)\]([\d\.]+)km \((\d+)/(\d+)\)(\d+).C to (\d+).C', infos_label)
        res = {}
        res['id'] = planet_id
        res['planet_name'] = infos.group(1)
        res['coordinate'] = {}
        res['coordinate']['galaxy'] = int(infos.group(2))
        res['coordinate']['system'] = int(infos.group(3))
        res['coordinate']['position'] = int(infos.group(4))
        res['diameter'] = int(infos.group(5).replace('.', ''))
        res['fields'] = {}
        res['fields']['built'] = int(infos.group(6))
        res['fields']['total'] = int(infos.group(7))
        res['temperature'] = {}
        res['temperature']['min'] = int(infos.group(8))
        res['temperature']['max'] = int(infos.group(9))
        return res

    def min_index(self, alist):
        return alist.index(min(alist))

    def planet_get_next_best_mine(self, planet_id, metalMineOffset, crystalMineOffset):
        planet_resources_buildings = self.get_resources_buildings(planet_id)
        mines = [planet_resources_buildings['metal_mine']-metalMineOffset,planet_resources_buildings['crystal_mine']-crystalMineOffset,planet_resources_buildings['deuterium_synthesizer']]
	return (self.min_index(mines) + 1)

    def get_ogame_version(self):
        """Get ogame version on your server."""
        res = self.session.get(self.get_url('overview')).content
        soup = BeautifulSoup(res, "lxml")
        footer = soup.find('div', {'id': 'siteFooter'})
        version = footer.find('a').text.strip()
        return version
