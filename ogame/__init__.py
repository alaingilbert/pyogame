from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID
from bs4 import BeautifulSoup

import requests
import json


class OGame(object):
    def __init__(self, universe, username, password, domain='ogame.org'):
        self.session = requests.session()

        servers = self.get_servers(domain)
        self.server_url = self.get_universe_url(universe, servers)
        self.username = username
        self.password = password
        self.login()


    def login(self):
        """Get the ogame session token."""
        payload = {'kid': '',
                   'uni': self.server_url,
                   'login': self.username,
                   'pass': self.password}
        res = self.session.post(self.get_url('login'), data=payload).content
        soup = BeautifulSoup(res)
        self.ogame_session = soup.find('meta', {'name': 'ogame-session'}) \
                                 .get('content')


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
        return json.loads(res)


    def fetch_resources(self, planet_id):
        url = self.get_url('fetchResources', planet_id)
        res = self.session.get(url).content
        return json.loads(res)


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


    def is_under_attack(self):
        json = self.fetch_eventbox()
        return not json.get('hostile', 0) == 0


    def get_planet_ids(self):
        """Get the ids of your planets."""
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

        url = self.get_url('defense', planet_id)

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

        url = self.get_url('shipyard', planet_id)

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

        url = self.get_url('resources', planet_id)

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'modus': 1,
                   'token': token,
                   'type': building_id}
        self.session.post(url, data=payload)


    def build_technology(self, planet_id, technology_id):
        if technology_id not in constants.Research.values():
            raise BAD_RESEARCH_ID

        url = self.get_url('research', planet_id)

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

        url = self.get_url('fleet1', planet_id)

        res = self.session.get(url).content
        payload= {}
        payload.update(get_hidden_fields(res))
        for name, value in ships:
            payload['am%s' % name] = value
        res = self.session.post(self.get_url('fleet2'), data=payload).content

        payload= {}
        payload.update(get_hidden_fields(res))
        payload.update({'speed': speed,
                        'galaxy': where.get('galaxy'),
                        'system': where.get('system'),
                        'position': where.get('position')})
        res = self.session.post(self.get_url('fleet3'), data=payload).content

        payload= {}
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
        soup = BeautifulSoup(res)
        spans = soup.findAll('span', {'class': 'reversal'})
        fleet_ids = [span.get('ref') for span in spans]
        return fleet_ids


    def get_url(self, page, planet_id=None):
        if page == 'login':
            return 'http://%s/game/reg/login2.php' % self.server_url
        else:
            url = 'http://%s/game/index.php?page=%s' % (self.server_url, page)
            if planet_id:
                url += '&cp=%s' % planet_id
            return url


    def get_servers(self, domain):
        res = self.session.get('http://%s' % domain).content
        soup = BeautifulSoup(res)
        select = soup.find('select', {'id': 'serverLogin'})
        servers = {}
        for opt in select.findAll('option'):
            url = opt.get('value')
            name = opt.string.strip().lower()
            servers[name] = url
        return servers


    def get_universe_url(self, universe, servers):
        """Get a universe name and return the server url."""
        universe = universe.lower()
        if universe not in servers:
            raise BAD_UNIVERSE_NAME
        return servers[universe]
