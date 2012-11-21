from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID
from bs4 import BeautifulSoup

import requests
import json


class OGame(object):
    def __init__(self, universe, username, password, domain='ogame.org'):
        self.session = requests.session()
        self.servers = self.get_servers(domain)
        self.username = username
        self.password = password
        self.server_url = self.get_universe_url(universe)
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


    def get_missions(self):
        res = self.session.get(self.get_url('fetchEventbox')).content
        return json.loads(res)


    def get_resources(self, planet_id):
        url = self.get_url('fetchResources') + '&cp=%s' % planet_id
        res = self.session.get(url).content
        return json.loads(res)


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

        url = self.get_url('defense') + '&cp=%s' % planet_id

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

        url = self.get_url('shipyard') + '&cp=%s' % planet_id

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

        url = self.get_url('resources') + '&cp=%s' % planet_id

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

        url = self.get_url('research') + '&cp=%s' % planet_id

        payload = {'modus': 1,
                   'type': technology_id}
        self.session.post(url, data=payload)


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

        url = self.get_url('fleet1') + '&cp=%s' % planet_id

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
        self.session.post(self.get_url('movement'), data=payload).content


    def get_url(self, name):
        if name == 'login':
            return 'http://%s/game/reg/login2.php' % self.server_url
        else:
            return 'http://%s/game/index.php?page=%s' % (self.server_url, name)


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


    def get_universe_url(self, universe):
        """Get a universe name and return the server url."""
        universe = universe.lower()
        if universe not in self.servers:
            raise BAD_UNIVERSE_NAME
        return self.servers[universe]
