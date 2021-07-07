import re
import requests
import unittest
from bs4 import BeautifulSoup
from datetime import datetime

try:
    import constants as const
except ImportError:
    import ogame.constants as const


class OGame(object):
    def __init__(
            self,
            universe,
            username,
            password,
            token=None, user_agent=None, proxy='',
            language=None, server_number=None
    ):
        self.universe = universe
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.proxy = proxy
        self.language = language
        self.server_number = server_number
        self.session = requests.Session()
        self.session.proxies.update({'https': self.proxy})
        self.token = token
        if self.user_agent is None:
            self.user_agent = {
                'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
            }
        self.session.headers.update(self.user_agent)

        if token is None:
            self.login()
        else:
            self.session.headers.update(
                {'authorization': 'Bearer {}'.format(token)}
            )
            accounts = self.session.get(
                url='https://lobby.ogame.gameforge.com'
                    '/api/users/me/accounts'
            ).json()
            if 'error' in accounts:
                del self.session.headers['authorization']
                self.login()

        servers = self.session.get(
            url='https://lobby.ogame.gameforge.com/api/servers'
        ).json()
        for server in servers:
            if server['name'] == self.universe:
                self.server_number = server['number']
                break
            elif server['name'] == self.universe and self.language is None:
                self.server_number = server['number']
                break
        assert self.server_number is not None, "Universe not found"

        accounts = self.session.get(
            url='https://lobby.ogame.gameforge.com/api/users/me/accounts'
        ).json()
        for account in accounts:
            if account['server']['number'] == self.server_number \
                    and account['server']['language'] == self.language:
                self.server_id = account['id']
                break
            elif account['server']['number'] == self.server_number \
                    and self.language is None:
                self.server_id = account['id']
                self.language = account['server']['language']
                break

        self.index_php = 'https://s{}-{}.ogame.gameforge.com/game/index.php?' \
            .format(self.server_number, self.language)
        login_link = self.session.get(
            url='https://lobby.ogame.gameforge.com/api/users/me/loginLink?',
            params={'id': self.server_id,
                    'server[language]': self.language,
                    'server[number]': self.server_number,
                    'clickedButton': 'account_list'}
        ).json()
        self.landing_page = self.session.get(login_link['url']).text
        self.landing_page = self.session.get(
            self.index_php + 'page=ingame'
        ).text
        self.landing_page = BeautifulSoup4(self.landing_page)

        self.player = self.landing_page.find(
            'meta', {'name': 'ogame-player-name'}
        )['content']
        self.player_id = int(self.landing_page.find(
            'meta', {'name': 'ogame-player-id'}
        )['content'])

    def login(self):
        self.session.get('https://lobby.ogame.gameforge.com/')
        login_data = {
            'identity': self.username,
            'password': self.password,
            'locale': 'en_EN',
            'gfLang': 'en',
            'platformGameId': '1dfd8e7e-6e1a-4eb1-8c64-03c3b62efd2f',
            'gameEnvironmentId': '0a31d605-ffaf-43e7-aa02-d06df7116fc8',
            'autoGameAccountCreation': False
        }
        response = self.session.post(
            'https://gameforge.com/api/v1/auth/thin/sessions',
            json=login_data
        )
        if response.status_code == 409:
            self.solveCaptcha(
                response.headers['gf-challenge-id']
                .replace(';https://challenge.gameforge.com', '')
            )
            self.login()
            return True
        assert response.status_code != 409, 'Resolve the Captcha'
        assert response.status_code == 201, 'Bad Login'
        self.token = response.json()['token']
        self.session.headers.update(
            {'authorization': 'Bearer {}'.format(self.token)}
        )


    def solveCaptcha(self, challenge):

        response = self.session.post(
            url='https://image-drop-challenge.gameforge.com/challenge/{}/en-GB'
                .format(challenge),
            json={"answer": 0}
        ).json()
        if response['status'] == 'solved':
            return True
        else:
            self.solveCaptcha(challenge)


    def test(self):
        import ogame.test
        ogame.test.UnittestOgame.empire = self
        suite = unittest.TestLoader().loadTestsFromModule(ogame.test)
        return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    def server(self):
        class Server:
            version = self.landing_page.find('meta', {'name': 'ogame-version'})

            class Speed:
                universe = self.landing_page.find(
                    'meta', {'name': 'ogame-universe-speed'}
                )
                universe = int(universe['content'])
                fleet = self.landing_page.find(
                    'meta', {'name': 'ogame-universe-speed-fleet'}
                )
                fleet = int(fleet['content'])

            class Donut:
                galaxy = self.landing_page.find(
                    'meta', {'name': 'ogame-donut-galaxy'}
                )['content']
                if 1 == int(galaxy):
                    galaxy = True
                else:
                    galaxy = False
                system = self.landing_page.find(
                    'meta', {'name': 'ogame-donut-system'}
                )['content']
                if 1 == int(system):
                    system = True
                else:
                    system = False

        return Server

    def attacked(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly'
                '&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['hostile']:
            return True
        else:
            return False

    def neutral(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly'
                '&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['neutral']:
            return True
        else:
            return False

    def friendly(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly'
                '&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['friendly']:
            return True
        else:
            return False

    def character_class(self):
        character = self.landing_page.find_partial(
            class_='sprite characterclass medium')
        return character['class'][3]

    def rank(self):
        rank = self.landing_page.find(id='bar')
        rank = rank.find_all('li')[1].text
        rank = re.search(r'\((.*)\)', rank).group(1)
        return int(rank)

    def numbers_planets(self):
        class Planets:
            nb_planets = self.landing_page.find('p', attrs={'class': 'textCenter'}).find('span').text
            free = int(nb_planets.split('/')[1]) - int(nb_planets.split('/')[0])
            total = int(nb_planets.split('/')[1])
        return Planets

    def planet_ids(self):
        ids = []
        for celestial in self.landing_page.find_all(class_='smallplanet'):
            ids.append(int(celestial['id'].replace('planet-', '')))
        return ids

    def planet_names(self):
        return [planet.text for planet in
                self.landing_page.find_all(class_='planet-name')]

    def id_by_planet_name(self, name):
        for planet_name, id in zip(
                OGame.planet_names(self), OGame.planet_ids(self)
        ):
            if planet_name == name:
                return id

    def name_by_planet_id(self, id):
        for _id, planet_name in zip(
                OGame.planet_ids(self), OGame.planet_names(self)
        ):
            if id == _id:
                return planet_name

    def moon_ids(self):
        moons = []
        for moon in self.landing_page.find_all(class_='moonlink'):
            moon = moon['href']
            moon = re.search('cp=(.*)', moon).group(1)
            moons.append(int(moon))
        return moons

    def moon_names(self):
        names = []
        for name in self.landing_page.find_all(class_='moonlink'):
            name = name['title']
            names.append(re.search(r'<b>(.*) \[', name).group(1))
        return names

    def slot_celestial(self):
        class Slot:
            planets = self.landing_page.find(
                'p',
                attrs={'class': 'textCenter'}
            ).find('span').text.split('/')
            planets = [int(planet) for planet in planets]
            free = planets[1] - planets[0]
            total = planets[1]
        return Slot

    def celestial(self, id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=overview',
            params={'cp': id}
        ).text
        textContent1 = re.search(
            r'textContent\[1] = "(.*)km \(<span>(.*)<(.*)<span>(.*)<',
            response
        )
        querys = [
            re.compile(r'textContent\[3] = "(.*) \\u00b0C \\u00e0(.*)(.*)\\'),
            re.compile(r'textContent\[3] = "(.*) \\u00b0C (.*) (.*) \\u00b0C"'),
        ]
        textContent3 = None
        for query in querys:
            textContent3 = query.search(
                response
            )
            if textContent3 is not None:
                break

        class Celestial:
            diameter = int(textContent1.group(1).replace('.', ''))
            used = int(textContent1.group(2))
            total = int(textContent1.group(4))
            free = total - used
            temperature = [
                int(textContent3.group(1)),
                int(textContent3.group(2))
            ]
            coordinates = OGame.celestial_coordinates(self, id)

        return Celestial

    def celestial_coordinates(self, id):
        for celestial in self.landing_page.find_all(class_='smallplanet'):
            planet = celestial.find(class_='planetlink')
            if str(id) in planet['href']:
                coordinates = re.search(r'\[(.*)]', planet['title']).group(1)
                coordinates = [int(coords) for coords in coordinates.split(':')]
                coordinates.append(const.destination.planet)
                return coordinates
            moon = celestial.find(class_='moonlink')
            if moon and str(id) in moon['href']:
                coordinates = re.search(r'\[(.*)]', moon['title']).group(1)
                coordinates = [int(coords) for coords in coordinates.split(':')]
                coordinates.append(const.destination.moon)
                return coordinates

    def resources(self, id):
        response = self.session.get(
            self.index_php + 'page=resourceSettings&cp={}'.format(id)
        ).text
        bs4 = BeautifulSoup4(response)

        def to_int(string):
            return int(float(string.replace('M', '000').replace('n', '')))

        class Resources:
            resources = [bs4.find(id='resources_metal')['data-raw'],
                         bs4.find(id='resources_crystal')['data-raw'],
                         bs4.find(id='resources_deuterium')['data-raw']]
            resources = [to_int(resource) for resource in resources]
            metal = resources[0]
            crystal = resources[1]
            deuterium = resources[2]
            day_production = bs4.find(
                'tr',
                attrs={'class':'summary'}
            ).find_all(
                'td',
                attrs={'class':'undermark'}
            )
            day_production = [
                int(day_production[0].span['title'].replace('.','')),
                int(day_production[1].span['title'].replace('.','')),
                int(day_production[2].span['title'].replace('.',''))
            ]
            storage = bs4.find_all('tr')
            for stor in storage:
                if len(stor.find_all('td', attrs={'class': 'left2'})) != 0:
                    storage = stor.find_all('td', attrs={'class': 'left2'})
                    break
            storage = [
                int(storage[0].span['title'].replace('.', '')),
                int(storage[1].span['title'].replace('.', '')),
                int(storage[2].span['title'].replace('.', ''))
            ]
            darkmatter = to_int(bs4.find(id='resources_darkmatter')['data-raw'])
            energy = to_int(bs4.find(id='resources_energy')['data-raw'])

        return Resources

    def isPossible(self: str):
        if self == 'on':
            return True
        else:
            return False

    def inConstruction(self):
        if self == 'active':
            return True
        else:
            return False

    def supply(self, id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=supplies&cp={}'
                .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        levels = [
            int(level['data-value'])
            for level in bs4.find_all('span', {'data-value': True})
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Supply:
            def __init__(self, i):
                self.level = levels[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Supplies(object):
            metal_mine = Supply(0)
            crystal_mine = Supply(1)
            deuterium_mine = Supply(2)
            solar_plant = Supply(3)
            fusion_plant = Supply(4)
            metal_storage = Supply(7)
            crystal_storage = Supply(8)
            deuterium_storage = Supply(9)

        return Supplies

    def facilities(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=facilities&cp={}'
            .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Facility:
            def __init__(self, i):
                self.level = levels[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Facilities(object):
            robotics_factory = Facility(0)
            shipyard = Facility(1)
            research_laboratory = Facility(2)
            alliance_depot = Facility(3)
            missile_silo = Facility(4)
            nanite_factory = Facility(5)
            terraformer = Facility(6)
            repair_dock = Facility(7)

        return Facilities

    def moon_facilities(self, id):
        response = self.session.get(
            url='{}page=ingame&component=facilities&cp={}'
                .format(self.index_php, id)
        ).text
        bs4 = BeautifulSoup4(response)
        levels = [
            int(level['data-value'])
            for level in bs4.find_all(class_=['targetlevel', 'level']) if level.get('data-value')
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Facility:
            def __init__(self, i):
                self.level = levels[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Facilities(object):
            robotics_factory = Facility(0)
            shipyard = Facility(1)
            moon_base = Facility(2)
            sensor_phalanx = Facility(3)
            jump_gate = Facility(4)

        return Facilities

    def traider(self, id):
        raise NotImplementedError("function not implemented yet PLS contribute")

    def research(self, id):
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'research',
                    'cp': id}
        ).text
        bs4 = BeautifulSoup4(response)
        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Research:
            def __init__(self, i):
                self.level = levels[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Researches(object):
            energy = Research(0)
            laser = Research(1)
            ion = Research(2)
            hyperspace = Research(3)
            plasma = Research(4)
            combustion_drive = Research(5)
            impulse_drive = Research(6)
            hyperspace_drive = Research(7)
            espionage = Research(8)
            computer = Research(9)
            astrophysics = Research(10)
            research_network = Research(11)
            graviton = Research(12)
            weapons = Research(13)
            shielding = Research(14)
            armor = Research(15)

        return Researches

    def ships(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=shipyard&cp={}'
            .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        ships_amount = [
            int(level['data-value'])
            for level in bs4.find_all(class_='amount')
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Ship:
            def __init__(self, i):
                self.amount = ships_amount[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Crawler:
            if id not in OGame.moon_ids(self):
                amount = ships_amount[16]
                self.is_possible = OGame.isPossible(technologyStatus[16])
                self.in_construction = OGame.inConstruction(
                    technologyStatus[16]
                )
            else:
                amount = 0
                is_possible = False
                in_construction = False

        class Ships(object):
            light_fighter = Ship(0)
            heavy_fighter = Ship(1)
            cruiser = Ship(2)
            battleship = Ship(3)
            interceptor = Ship(4)
            bomber = Ship(5)
            destroyer = Ship(6)
            deathstar = Ship(7)
            reaper = Ship(8)
            explorer = Ship(9)
            small_transporter = Ship(10)
            large_transporter = Ship(11)
            colonyShip = Ship(12)
            recycler = Ship(13)
            espionage_probe = Ship(14)
            solarSatellite = Ship(15)
            crawler = Crawler

        return Ships

    def defences(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=defenses&cp={}'
            .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        defences_amount = [
            int(level['data-value'])
            for level in bs4.find_all(class_='amount')
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]

        class Defence:
            def __init__(self, i):
                self.amount = defences_amount[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class Defences(object):
            rocket_launcher = Defence(0)
            laser_cannon_light = Defence(1)
            laser_cannon_heavy = Defence(2)
            gauss_cannon = Defence(3)
            ion_cannon = Defence(4)
            plasma_cannon = Defence(5)
            shield_dome_small = Defence(6)
            shield_dome_large = Defence(7)
            missile_interceptor = Defence(8)
            missile_interplanetary = Defence(9)

        return Defences

    def galaxy(self, coords):
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=galaxyContent&ajax=1',
            data={'galaxy': coords[0], 'system': coords[1]},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        bs4 = BeautifulSoup4(response['galaxy'])

        def playerId(tag):
            numbers = re.search(r'[0-9]+', tag).group()
            return int(numbers)

        players = bs4.find_all_partial(id='player')
        player_name = {
            playerId(player['id']): player.h1.span.text
            for player in players
        }
        player_rank = {
            playerId(player['id']): int(player.a.text)
            for player in players if player.a.text.isdigit()
        }

        alliances = bs4.find_all_partial(id='alliance')
        alliance_name = {
            playerId(alliance['id']): alliance.h1.text.strip()
            for alliance in alliances
        }

        planets = []
        for row in bs4.select('#galaxytable .row'):
            status = row['class']
            status.remove('row')
            if 'empty_filter' in status:
                continue
            elif len(status) == 0:
                planet_status = [const.status.yourself]
                pid = self.player_id
                player_name[pid] = self.player
            else:
                planet_status = [
                    re.search('(.*)_filter', sta).group(1)
                    for sta in status
                ]

                player = row.find(rel=re.compile(r'player[0-9]+'))
                if not player:
                    continue
                pid = playerId(player['rel'][0])
                if pid == const.status.destroyed:
                    continue

            planet = int(row.find(class_='position').text)
            planet_cord = const.coordinates(coords[0], coords[1], int(planet))
            moon_pos = row.find(rel=re.compile(r'moon[0-9]*'))

            alliance_id = row.find(rel=re.compile(r'alliance[0-9]+'))
            alliance_id = playerId(
                alliance_id['rel']) if alliance_id else None

            class Position:
                position = planet_cord
                name = row.find(id=re.compile(r'planet[0-9]+')).h1.span.text
                player = player_name[pid]
                player_id = pid
                rank = player_rank.get(pid)
                status = planet_status
                moon = moon_pos is not None
                alliance = alliance_name.get(alliance_id)
                list = [
                    name, position, player,
                    player_id, rank, status, moon, alliance
                ]

            planets.append(Position)

        return planets

    def ally(self):
        alliance = self.landing_page.find(name='ogame-alliance-name')
        if alliance:
            return alliance
        else:
            return []

    def officers(self):
        raise NotImplementedError("function not implemented yet PLS contribute")

    def shop(self):
        raise NotImplementedError("function not implemented yet PLS contribute")

    def fleet_coordinates(self, event, Coords):
        coordinate = [
            coords.find(class_=Coords).a.text
            for coords in event
        ]
        coordinate = [
            const.convert_to_coordinates(coords)
            for coords in coordinate
        ]
        destination = [
            dest.find('figure', {'class': 'planetIcon'})
            for dest in event
        ]
        destination = [
            const.convert_to_destinations(dest['class'])
            for dest in destination
        ]
        coordinates = []
        for coords, dest in zip(coordinate, destination):
            coords.append(dest)
            coordinates.append(coords)

        return coordinates

    def slot_fleet(self):
        response = self.session.get(
            self.index_php + 'page=ingame&component=fleetdispatch'
        ).text
        bs4 = BeautifulSoup4(response)
        slots = bs4.find('div', attrs={'id':'slots', 'class': 'fleft'})
        slots = [
            slot.text
            for slot in slots.find_all(class_="fleft")
        ]
        fleet = re.search(':(.*)/(.*)', slots[0])
        fleet = [fleet.group(1), fleet.group(2)]
        expedition = re.search(' (.*)/(.*)\\n', slots[1])
        expedition = [
            expedition.group(1).replace(' ', ''),
            expedition.group(2)
        ]

        class Fleet:
            total = int(fleet[1])
            free = total - int(fleet[0])

        class Expedition:
            total = int(expedition[1])
            free = total - int(expedition[0])

        class Slot:
            fleet = Fleet
            expedition = Expedition

        return Slot

    def fleet(self):
        fleets = []
        fleets.extend(self.hostile_fleet())
        fleets.extend(self.friendly_fleet())
        return fleets

    def friendly_fleet(self):
        if not self.friendly():
            return []
        response = self.session.get(
            self.index_php + 'page=ingame&component=movement'
        ).text
        bs4 = BeautifulSoup4(response)
        fleetDetails = bs4.find_all(class_='fleetDetails')
        fleet_ids = bs4.find_all_partial(id="fleet")
        fleet_ids = [id['id'] for id in fleet_ids]
        fleet_ids = [
            int(re.search('fleet(.*)', id).group(1))
            for id in fleet_ids
        ]

        mission_types = [
            int(event['data-mission-type'])
            for event in fleetDetails
        ]
        return_flights = [
            bool(event['data-return-flight'])
            for event in fleetDetails
        ]
        arrival_times = [
            int(event['data-arrival-time'])
            for event in fleetDetails
        ]
        arrival_times = [
            datetime.fromtimestamp(timestamp)
            for timestamp in arrival_times
        ]

        destinations = self.fleet_coordinates(fleetDetails, 'destinationCoords')
        origins = self.fleet_coordinates(fleetDetails, 'originCoords')

        fleets = []
        for i in range(len(fleet_ids)):
            class Fleets:
                id = fleet_ids[i]
                mission = mission_types[i]
                diplomacy = const.diplomacy.friendly
                player_name = self.player
                player_id = self.player_id
                returns = return_flights[i]
                arrival = arrival_times[i]
                origin = origins[i]
                destination = destinations[i]
                list = [id, mission, diplomacy, player_name, player_id, returns,
                        arrival, origin, destination]

            fleets.append(Fleets)
        return fleets

    def hostile_fleet(self):
        if not self.attacked():
            return []
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList'
        ).text
        bs4 = BeautifulSoup4(response)

        eventFleet = bs4.find_all('span', class_='hostile')
        eventFleet = [child.parent.parent for child in eventFleet]

        fleet_ids = [id['id'] for id in eventFleet]
        fleet_ids = [
            int(re.search('eventRow-(.*)', id).group(1))
            for id in fleet_ids
        ]

        arrival_times = [
            int(event['data-arrival-time'])
            for event in eventFleet
        ]
        arrival_times = [
            datetime.fromtimestamp(timestamp)
            for timestamp in arrival_times
        ]

        destinations = self.fleet_coordinates(eventFleet, 'destCoords')
        origins = self.fleet_coordinates(eventFleet, 'coordsOrigin')

        player_ids = [
            int(id.find(class_='sendMail').a['data-playerid'])
            for id in eventFleet
        ]
        player_names = [
            name.find(class_='sendMail').a['title']
            for name in eventFleet
        ]

        fleets = []
        for i in range(len(fleet_ids)):
            class Fleets:
                id = fleet_ids[i]
                mission = 1
                diplomacy = const.diplomacy.hostile
                player_name = player_names[i]
                player_id = player_ids[i]
                returns = False
                arrival = arrival_times[i]
                origin = origins[i]
                destination = destinations[i]
                list = [id, mission, diplomacy, player_name, player_id, returns,
                        arrival, origin, destination]

            fleets.append(Fleets)
        return fleets

    def phalanx(self, coordinates, id):
        raise NotImplemented(
            'Phalanx get you banned if used with invalid parameters')

    def send_message(self, player_id, msg):
        response = self.session.get(self.index_php + 'page=chat').text
        chat_token = re.search('var ajaxChatToken = "(.*)"', response).group(1)
        response = self.session.post(
            url=self.index_php + 'page=ajaxChat',
            data={'playerId': player_id,
                  'text': msg,
                  'mode': 1,
                  'ajax': 1,
                  'token': chat_token},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 'OK' in response['status']:
            return True
        else:
            return False

    def rename_planet(self, id, new_name):
        self.session.get(
            url=self.index_php,
            params={'cp': id})
        response = self.session.get(self.index_php,
                                    params={'page': 'planetlayer'},
                                    headers={'Referer': f'{self.index_php}page=ingame&component=overview&cp={id}'}).text
        token_rename = re.search("name='token' value='(.*)'", response).group(1)
        param = {'page': 'planetRename'}
        data = {
            'newPlanetName': new_name,
            'token': token_rename}
        response = self.session.post(
            url=self.index_php,
            params=param,
            data=data,
            headers={'Referer': f'{self.index_php}page=ingame&component=overview&cp={id}'}
        ).json()
        return response['status']

    def abandon_planet(self, id):
        self.session.get(
            url=self.index_php,
            params={'cp': id})
        header = {'Referer': f'{self.index_php}page=ingame&component=overview&cp={id}'}
        response = self.session.get(self.index_php,
                                    params={'page': 'planetlayer'},
                                    headers=header).text
        response = response[response.find('input type="hidden" name="abandon" value="'):]
        code_abandon = re.search('name="abandon" value="(.*)"', response).group(1)
        token_abandon = re.search("name='token' value='(.*)'", response).group(1)
        response = self.session.post(url=self.index_php,
                                     params={
                                         'page': 'checkPassword'
                                     },
                                     data={
                                         'abandon': code_abandon,
                                         'token': token_abandon,
                                         'password': self.password,
                                     },
                                     headers=header).json()
        new_token = None
        if (
                response.get("password_checked")
                and response["password_checked"] == True
        ):
            new_token = response["newToken"]
        if new_token:
            self.session.post(url=self.index_php,
                              params={
                                  'page': 'planetGiveup'
                              },
                              data={
                                  'abandon': code_abandon,
                                  'token': new_token,
                                  'password': self.password,
                              },
                              headers=header).json()

    def spyreports(self, lastDateOfReport=None, firstpage=1, lastpage=30):
        # get links for the last 30 pages
        report_links = []
        while firstpage <= lastpage:
            try:
                response = self.session.get(
                    url=self.index_php,
                    params={'page': 'messages',
                            'tab': 20,
                            'action': 107,
                            'messageId': -1,
                            'pagination': firstpage,
                            'ajax': 1}
                ).text
            except:
                break
            bs4 = BeautifulSoup4(response)
            for link in bs4.find_all_partial(href='page=messages&messageId'):
                if link['href'] not in report_links:
                    report_links.extend([link['href'] for link in bs4.find_all_partial(href='page=messages&messageId')])
            firstpage += 1
        reports = []
        for link in report_links:
            response = self.session.get(link).text
            bs4 = BeautifulSoup4(response)
            technologys = [tech['class'][0] for tech in bs4.find_all('img')]
            amounts = [
                tech.parent.parent.find_all('span')[1].text
                for tech in bs4.find_all('img')
            ]

            class Report:
                fright = [
                    (tech, amount)
                    for tech, amount in zip(technologys, amounts)
                ]

            reports.append(Report)
        return reports

    def send_fleet(
            self,
            mission,
            id,
            where,
            ships,
            resources=(0, 0, 0), speed=10, holdingtime=0
    ):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=fleetdispatch&cp={}'
                .format(id)
        ).text
        send_fleet_token = re.search('var fleetSendingToken = "(.*)"', response)
        if send_fleet_token is None:
            send_fleet_token = re.search('var token = "(.*)"', response)
        form_data = {'token': send_fleet_token.group(1)}
        for ship in ships:
            ship_type = 'am{}'.format(ship[0])
            form_data.update({ship_type: ship[1]})
        form_data.update(
            {
                'galaxy': where[0],
                'system': where[1],
                'position': where[2],
                'type': where[3],
                'metal': resources[0],
                'crystal': resources[1],
                'deuterium': resources[2],
                'prioMetal': 1,
                'prioCrystal': 2,
                'prioDeuterium': 3,
                'mission': mission,
                'speed': speed,
                'retreatAfterDefenderRetreat': 0,
                'union': 0,
                'holdingtime': holdingtime
            }
        )
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=fleetdispatch'
                '&action=sendFleet&ajax=1&asJson=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        return response['success']

    def return_fleet(self, fleet_id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=movement'
        ).text
        if "return={}".format(fleet_id) in response:
            token = re.search(
                'return={}'.format(fleet_id)+'&amp;token=(.*)" ', response
            ).group(1).split('"')[0]
            self.session.get(
                url=''.join([
                    self.index_php,
                    'page=ingame&component=movement&return={}&token={}'
                    .format(fleet_id, token)
                ])
            )
            return True
        else:
            return False

    def build(self, what, id):
        type = what[0]
        amount = what[1]
        component = what[2]
        response = self.session.get(
            url=self.index_php +
                'page=ingame&component={}&cp={}'
                .format(component, id)
        ).text
        build_token = re.search(
            "var urlQueueAdd = (.*)token=(.*)';",
            response
        ).group(2)
        self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': component,
                    'modus': 1,
                    'token': build_token,
                    'type': type,
                    'menge': amount}
        )

    def collect_rubble_field(self, id):
        self.session.get(
            url=self.index_php +
                'page=ajax&component=repairlayer&component=repairlayer&ajax=1'
                '&action=startRepairs&asJson=1&cp={}'
                .format(id),
            headers={'X-Requested-With': 'XMLHttpRequest'})

    def is_logged_in(self):
        response = self.session.get(
            url='https://lobby.ogame.gameforge.com/api/users/me/accounts'
        ).json()
        if 'error' in response:
            return False
        else:
            return True

    def relogin(self, universe=None):
        if universe is None:
            universe = self.universe
        OGame.__init__(self, universe, self.username, self.password,
                       self.user_agent, self.proxy)
        return OGame.is_logged_in(self)

    def keep_going(self, function):
        try:
            function()
        except:
            self.relogin()
            function()

    def logout(self):
        self.session.get(self.index_php + 'page=logout')
        self.session.put(
            'https://lobby.ogame.gameforge.com/api/users/me/logout'
        )
        return not OGame.is_logged_in(self)


def BeautifulSoup4(response):
    parsed = BeautifulSoup(response, features="html5lib")

    def find_partial(**kwargs):
        for key, value in kwargs.items():
            kwargs[key] = re.compile(value)
        return parsed.find(**kwargs)

    def find_all_partial(**kwargs):
        for key, value in kwargs.items():
            kwargs[key] = re.compile(value)
        return parsed.find_all(**kwargs)

    parsed.find_partial = find_partial
    parsed.find_all_partial = find_all_partial
    return parsed
