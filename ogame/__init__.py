import re
import requests
import unittest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import math
import random

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
        self.user_agent = {'User-Agent': user_agent}
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
            self.solve_captcha(
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

    def solve_captcha(self, challenge):
        response = self.session.get(
            url='https://image-drop-challenge.gameforge.com/challenge/{}/en-GB'
                .format(challenge)
        ).json()
        assert response['status'] == 'presented'
        response = self.session.post(
            url='https://image-drop-challenge.gameforge.com/challenge/{}/en-GB'
                .format(challenge),
            json={"answer": 0}
        ).json()
        if response['status'] == 'solved':
            return True
        else:
            self.solve_captcha(challenge)

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
                    'meta', {'name': 'ogame-universe-speed-fleet-peaceful'}
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
        textContent3 = re.search(
            r'textContent\[3] = "(.*)"',
            response
        )
        textContent3 = textContent3.group(1).replace('\\u00b0', '')
        textContent3 = re.findall(r'\d+(?: \d+)?', textContent3)

        class Celestial:
            diameter = int(textContent1.group(1).replace('.', ''))
            used = int(textContent1.group(2))
            total = int(textContent1.group(4))
            free = total - used
            temperature = [
                textContent3[0],
                textContent3[1]
            ]
            coordinates = OGame.celestial_coordinates(self, id)

        return Celestial

    def celestial_queue(self, id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=overview',
            params={'cp': id}
        ).text
        research_time = re.search(r'var restTimeresearch = ([0-9]+)', response)
        if research_time is None:
            research_time = datetime.fromtimestamp(0)
        else:
            research_time = int(research_time.group(1))
            research_time = datetime.fromtimestamp(research_time)
        build_time = re.search(r'var restTimebuilding = ([0-9]+)', response)
        if build_time is None:
            build_time = datetime.fromtimestamp(0)
        else:
            build_time = int(build_time.group(1))
            build_time = datetime.fromtimestamp(build_time)
        shipyard_time = re.search(r'var restTimeship2 = ([0-9]+)', response)
        if shipyard_time is None:
            shipyard_time = datetime.fromtimestamp(0)
        else:
            shipyard_time = int(shipyard_time.group(1))
            shipyard_time = datetime.now() + timedelta(seconds=shipyard_time)
        class Queue:
            research = research_time
            buildings = build_time
            shipyard = shipyard_time
            list = [
                research,
                buildings,
                shipyard
            ]
        return Queue

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

    def resources_settings(self, id, settings=None):
        response = self.session.get(
            self.index_php + 'page=resourceSettings&cp={}'.format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        settings_form = {
            'saveSettings': 1,
        }
        token = bs4.find('input', {'name':'token'})['value']
        settings_form.update({'token': token})
        names = [
            'last1', 'last2', 'last3', 'last4',
            'last12', 'last212', 'last217'
        ]
        for building_name in names:
            select = bs4.find('select', {'name': building_name})
            selected_value = select.find('option', selected=True)['value']
            settings_form.update({building_name: selected_value})
        if settings is not None:
            for building, speed in settings.items():
                settings_form.update(
                    {'last{}'.format(building[0]): speed * 10}
                )
            self.session.post(
                self.index_php + 'page=resourceSettings&cp={}'.format(id),
                data=settings_form
            )
        settings_data = {}
        for key, value in settings_form.items():
            if key in names:
                building_id = int(key.replace('last', ''))
                building_name = const.buildings.building_name(
                    (building_id, 1, 'supplies')
                )
                settings_data[building_name] = value

        class Settings:
            metal_mine = settings_data['metal_mine']
            crystal_mine = settings_data['crystal_mine']
            deuterium_mine = settings_data['deuterium_mine']
            solar_plant = settings_data['solar_plant']
            fusion_plant = settings_data['fusion_plant']
            solar_satellite = settings_data['solar_satellite']
            crawler = settings_data['crawler']
            list = [
                metal_mine, crystal_mine, deuterium_mine,
                solar_plant, fusion_plant, solar_satellite,
                crawler
            ]
        return Settings

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

    def research(self, id=None):
        if id is None:
            id = self.planet_ids()[0]
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
    
        def lf_research_humans(self, id=None):
        if id is None:
            id = self.planet_ids()[0]
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'lfresearch',
                    'cp': id}
        ).text
        bs4 = BeautifulSoup4(response)

        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]

        technology_status = []
        for container_tiers in bs4.select('#technologies div li'):
            try:
                technology_status.append(container_tiers['data-status'])
            except:
                technology_status.append('not available')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on') + technology_status.count('disabled') - 1:
                    self.level = levels[i]
                    self.is_possible = OGame.isPossible(technology_status[i])
                    self.in_construction = OGame.inConstruction(technology_status[i])
                else:
                    self.level = 0
                    self.is_possible = False
                    self.in_construction = False

        class LfResearches(object):
            intergalactic_envoys = LfResearch(0)
            high_performance_extractors = LfResearch(1)
            fusion_drives = LfResearch(2)
            stealth_field_generator = LfResearch(3)
            orbital_den = LfResearch(4)
            research_ai = LfResearch(5)
            high_performance_terraformer = LfResearch(6)
            enhanced_production_technologies = LfResearch(7)
            light_fighter_mk_II = LfResearch(8)
            cruiser_mk_II = LfResearch(9)
            improved_lab_technology = LfResearch(10)
            plasma_terraformer = LfResearch(11)
            low_temperature_drives = LfResearch(12)
            bomber_mk_II = LfResearch(13)
            destroyer_mk_II = LfResearch(14)
            battlecruiser_mk_II = LfResearch(15)
            robot_assistants = LfResearch(16)
            supercomputer = LfResearch(17)
            list = {
                'intergalactic_envoys': intergalactic_envoys.level,
                'high_performance_extractors': high_performance_extractors.level,
                'fusion_drives': fusion_drives.level,
                'stealth_field_generator': stealth_field_generator.level,
                'orbital_den': orbital_den.level,
                'research_ai': research_ai.level,
                'high_performance_terraformer': high_performance_terraformer.level,
                'enhanced_production_technologies': enhanced_production_technologies.level,
                'light_fighter_mk_II': light_fighter_mk_II.level,
                'cruiser_mk_II': cruiser_mk_II.level,
                'improved_lab_technology': improved_lab_technology.level,
                'plasma_terraformer': plasma_terraformer.level,
                'low_temperature_drives': low_temperature_drives.level,
                'bomber_mk_II': bomber_mk_II.level,
                'destroyer_mk_II': destroyer_mk_II.level,
                'battlecruiser_mk_II': battlecruiser_mk_II.level,
                'robot_assistants': robot_assistants.level,
                'supercomputer': supercomputer.level
            }

        return LfResearches

    def lf_research_rocktal(self, id=None):
        if id is None:
            id = self.planet_ids()[0]
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'lfresearch',
                    'cp': id}
        ).text
        bs4 = BeautifulSoup4(response)

        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]

        technology_status = []
        for container_tiers in bs4.select('#technologies div li'):
            try:
                technology_status.append(container_tiers['data-status'])
            except:
                technology_status.append('not available')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on') + technology_status.count('disabled') - 1:
                    self.level = levels[i]
                    self.is_possible = OGame.isPossible(technology_status[i])
                    self.in_construction = OGame.inConstruction(technology_status[i])
                else:
                    self.level = 0
                    self.is_possible = False
                    self.in_construction = False

        class LfResearches(object):
            magma_refinement = LfResearch(0)
            acoustic_scanning = LfResearch(1)
            high_energy_pump_systems = LfResearch(2)
            cargo_hold_expansion_civilian_ships = LfResearch(3)
            magma_powered_production = LfResearch(4)
            geothermal_power_plants = LfResearch(5)
            depth_sounding = LfResearch(6)
            ion_crystal_enhancement_heavy_fighter = LfResearch(7)
            improved_stellarator = LfResearch(8)
            hardened_diamond_drill_heads = LfResearch(9)
            seismic_mining_technology = LfResearch(10)
            magma_powered_pump_systems = LfResearch(11)
            ion_crystal_modules = LfResearch(12)
            optimised_silo_construction_method = LfResearch(13)
            diamond_energy_transmitter = LfResearch(14)
            obsidian_shield_reinforcement = LfResearch(15)
            rocktal_collector_enhancement = LfResearch(16)
            rune_shields = LfResearch(17)

            list = {
                'magma_refinement': magma_refinement.level,
                'acoustic_scanning': acoustic_scanning.level,
                'high_energy_pump_systems': high_energy_pump_systems.level,
                'cargo_hold_expansion_civilian_ships': cargo_hold_expansion_civilian_ships.level,
                'magma_powered_production': magma_powered_production.level,
                'geothermal_power_plants': geothermal_power_plants.level,
                'depth_sounding': depth_sounding.level,
                'ion_crystal_enhancement_heavy_fighter': ion_crystal_enhancement_heavy_fighter.level,
                'improved_stellarator': improved_stellarator.level,
                'hardened_diamond_drill_heads': hardened_diamond_drill_heads.level,
                'seismic_mining_technology': seismic_mining_technology.level,
                'magma_powered_pump_systems': magma_powered_pump_systems.level,
                'ion_crystal_modules': ion_crystal_modules.level,
                'optimised_silo_construction_method': optimised_silo_construction_method.level,
                'diamond_energy_transmitter': diamond_energy_transmitter.level,
                'obsidian_shield_reinforcement': obsidian_shield_reinforcement.level,
                'rocktal_collector_enhancement': rocktal_collector_enhancement.level,
                'rune_shields': rune_shields.level
            }

        return LfResearches

    def lf_research_mechas(self, id=None):
        if id is None:
            id = self.planet_ids()[0]
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'lfresearch',
                    'cp': id}
        ).text
        bs4 = BeautifulSoup4(response)

        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]

        technology_status = []
        for container_tiers in bs4.select('#technologies div li'):
            try:
                technology_status.append(container_tiers['data-status'])
            except:
                technology_status.append('not available')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on') + technology_status.count('disabled') - 1:
                    self.level = levels[i]
                    self.is_possible = OGame.isPossible(technology_status[i])
                    self.in_construction = OGame.inConstruction(technology_status[i])
                else:
                    self.level = 0
                    self.is_possible = False
                    self.in_construction = False

        class LfResearches(object):
            catalyser_technology = LfResearch(0)
            plasma_drive = LfResearch(1)
            efficiency_module = LfResearch(2)
            depot_ai = LfResearch(3)
            general_overhaul_light_fighter = LfResearch(4)
            automated_transport_lines = LfResearch(5)
            improved_drone_ai = LfResearch(6)
            experimental_recycling_technology = LfResearch(7)
            general_overhaul_cruiser = LfResearch(8)
            slingshot_autopilot = LfResearch(9)
            high_temperature_superconductors = LfResearch(10)
            general_overhaul_battleship = LfResearch(11)
            artificial_swarm_intelligence = LfResearch(12)
            general_overhaul_battlecruiser = LfResearch(13)
            general_overhaul_bomber = LfResearch(14)
            general_overhaul_destroyer = LfResearch(15)
            mechan_general_enhancement = LfResearch(16)
            experimental_weapons_technology = LfResearch(17)

            list = {
                'catalyser_technology': catalyser_technology.level,
                'plasma_drive': plasma_drive.level,
                'efficiency_module': efficiency_module.level,
                'depot_ai': depot_ai.level,
                'general_overhaul_light_fighter': general_overhaul_light_fighter.level,
                'automated_transport_lines': automated_transport_lines.level,
                'improved_drone_ai': improved_drone_ai.level,
                'experimental_recycling_technology': experimental_recycling_technology.level,
                'general_overhaul_cruiser': general_overhaul_cruiser.level,
                'slingshot_autopilot': slingshot_autopilot.level,
                'high_temperature_superconductors': high_temperature_superconductors.level,
                'general_overhaul_battleship': general_overhaul_battleship.level,
                'artificial_swarm_intelligence': artificial_swarm_intelligence.level,
                'general_overhaul_battlecruiser': general_overhaul_battlecruiser.level,
                'general_overhaul_bomber': general_overhaul_bomber.level,
                'general_overhaul_destroyer': general_overhaul_destroyer.level,
                'mechan_general_enhancement': mechan_general_enhancement.level,
                'experimental_weapons_technology': experimental_weapons_technology.level
            }

        return LfResearches

    def lf_research_kaelesh(self, id=None):
        if id is None:
            id = self.planet_ids()[0]
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'lfresearch',
                    'cp': id}
        ).text
        bs4 = BeautifulSoup4(response)

        levels = [
            int(level['data-value'])
            for level in bs4.find_all(
                'span', {'class': 'level', 'data-value': True}
            )
        ]

        technology_status = []
        for container_tiers in bs4.select('#technologies div li'):
            try:
                technology_status.append(container_tiers['data-status'])
            except:
                technology_status.append('not available')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on') + technology_status.count('disabled') - 1:
                    self.level = levels[i]
                    self.is_possible = OGame.isPossible(technology_status[i])
                    self.in_construction = OGame.inConstruction(technology_status[i])
                else:
                    self.level = 0
                    self.is_possible = False
                    self.in_construction = False

        class LfResearches(object):
            heat_recovery = LfResearch(0)
            sulphide_process = LfResearch(1)
            psionic_network = LfResearch(2)
            telekinetic_tractor_beam = LfResearch(3)
            enhanced_sensor_technology = LfResearch(4)
            neuromodal_compressor = LfResearch(5)
            neuro_interface = LfResearch(6)
            interplanetary_analysis_network = LfResearch(7)
            overclocking_heavy_fighter = LfResearch(8)
            telekinetic_drive = LfResearch(9)
            sixth_sense = LfResearch(10)
            psychoharmoniser = LfResearch(11)
            efficient_swarm_intelligence = LfResearch(12)
            overclocking_large_cargo = LfResearch(13)
            gravitation_sensors = LfResearch(14)
            overclocking_battleship = LfResearch(15)
            kaelesh_discoverer_enhancement = LfResearch(16)
            psionic_shield_matrix = LfResearch(17)

            list = {
                'heat_recovery': heat_recovery.level,
                'sulphide_process': sulphide_process.level,
                'psionic_network': psionic_network.level,
                'telekinetic_tractor_beam': telekinetic_tractor_beam.level,
                'enhanced_sensor_technology': enhanced_sensor_technology.level,
                'neuromodal_compressor': neuromodal_compressor.level,
                'neuro_interface': neuro_interface.level,
                'interplanetary_analysis_network': interplanetary_analysis_network.level,
                'overclocking_heavy_fighter': overclocking_heavy_fighter.level,
                'telekinetic_drive': telekinetic_drive.level,
                'sixth_sense': sixth_sense.level,
                'psychoharmoniser': psychoharmoniser.level,
                'efficient_swarm_intelligence': efficient_swarm_intelligence.level,
                'overclocking_large_cargo': overclocking_large_cargo.level,
                'gravitation_sensors': gravitation_sensors.level,
                'overclocking_battleship': overclocking_battleship.level,
                'kaelesh_discoverer_enhancement': kaelesh_discoverer_enhancement.level,
                'psionic_shield_matrix': psionic_shield_matrix.level,
            }

        return LfResearches
    
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

    def galaxy_debris(self, coords):
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=galaxyContent&ajax=1',
            data={'galaxy': coords[0], 'system': coords[1]},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        bs4 = BeautifulSoup4(response['galaxy'])
        debris_fields = []
        debris_rows = bs4.find_all('td', {'class': 'debris'})
        for row in debris_rows:
            debris = True
            row['class'].remove('debris')
            if 'js_no_action' in row['class']:
                debris = False
                row['class'].remove('js_no_action')
            debris_cord = int(row['class'][0].replace('js_debris', ''))
            debris_cord = const.coordinates(
                coords[0],
                coords[1],
                int(debris_cord), const.destination.debris
            )
            debris_resources = [0, 0, 0]
            if debris:
                debris_resources = row.find_all('li', {'class': 'debris-content'})
                debris_resources = [
                    int(debris_resources[0].text.split(':')[1].replace('.','')),
                    int(debris_resources[1].text.split(':')[1].replace('.','')),
                    0
                ]

            class Position:
                position = debris_cord
                has_debris = debris
                resources = debris_resources
                metal = resources[0]
                crystal = resources[1]
                deuterium = resources[2]
                list = [
                    position, has_debris, resources,
                    metal, crystal, deuterium
                ]
            if len(coords) >= 3 and coords[2] == Position.position[2]:
                return Position
            debris_fields.append(Position)
        return debris_fields

    def ally(self):
        alliance = self.landing_page.find(name='ogame-alliance-name')
        if alliance:
            return alliance
        else:
            return []

    def officers(self):
        commander_element = self.landing_page.find_partial(class_='on commander')
        admiral_element = self.landing_page.find_partial(class_='on admiral')
        engineer_element = self.landing_page.find_partial(class_='on engineer')
        geologist_element = self.landing_page.find_partial(class_='on geologist')
        technocrat_element = self.landing_page.find_partial(class_='on technocrat')

        class Officers(object):
            commander = commander_element is not None
            admiral = admiral_element is not None
            engineer = engineer_element is not None
            geologist = geologist_element is not None
            technocrat = technocrat_element is not None

        return Officers

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
            for slot in slots.find_all(class_='fleft')
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
        fleet_ids = bs4.find_all_partial(id='fleet')
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
            re.search('eventRow-(.*)', id).group(1)
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
                list = [
                    id, mission, diplomacy, player_name, player_id, returns,
                    arrival, origin, destination
                ]

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
        response = self.session.get(
            url=self.index_php,
            params={'page': 'planetlayer'},
            headers={
                'Referer': f'{self.index_php}page=ingame'
                           f'&component=overview&cp={id}'
            }
        ).text
        token_rename = re.search("name='token' value='(.*)'", response).group(1)
        param = {'page': 'planetRename'}
        data = {
            'newPlanetName': new_name,
            'token': token_rename}
        response = self.session.post(
            url=self.index_php,
            params=param,
            data=data,
            headers={
                'Referer': f'{self.index_php}page=ingame'
                           f'&component=overview&cp={id}'
            }
        ).json()
        return response['status']

    def abandon_planet(self, id):
        self.session.get(
            url=self.index_php,
            params={'cp': id}
        )
        header = {
            'Referer': f'{self.index_php}page=ingame'
                       f'&component=overview&cp={id}'
        }
        response = self.session.get(
            self.index_php,
            params={'page': 'planetlayer'},
            headers=header
        ).text
        response = response[response.find('input type="hidden" name="abandon" value="'):]
        code_abandon = re.search(
            'name="abandon" value="(.*)"', response
        ).group(1)
        token_abandon = re.search(
            "name='token' value='(.*)'", response
        ).group(1)
        response = self.session.post(
            url=self.index_php,
            params={'page': 'checkPassword'},
            data={
                'abandon': code_abandon,
                'token': token_abandon,
                'password': self.password,
            },
            headers=header
        ).json()
        new_token = None
        if response.get("password_checked") and response["password_checked"]:
            new_token = response["newAjaxToken"]
        if new_token:
            self.session.post(
                url=self.index_php,
                params={
                    'page': 'planetGiveup'
                },
                data={
                    'abandon': code_abandon,
                    'token': new_token,
                    'password': self.password,
                },
                headers=header).json()
            self.session.get(url=self.index_php)
            return True
        else:
            return False

    def spyreports(self, firstpage=1, lastpage=30):
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
            except Exception as e:
                print(e)
                break
            bs4 = BeautifulSoup4(response)
            for link in bs4.find_all_partial(href='page=messages&messageId'):
                if link['href'] not in report_links:
                    report_links.append(link['href'])
            firstpage += 1
        reports = []
        for link in report_links:
            response = self.session.get(link).text
            bs4 = BeautifulSoup4(response)
            resources_list = bs4.find('ul', {'data-type': 'resources'})
            if resources_list is None:
                continue
            planet_coords = bs4.find('span', 'msg_title').find('a')
            if planet_coords is None:
                continue
            planet_coords = re.search(r'(.*?) (\[(.*?)])', planet_coords.text)
            report_datetime = bs4.find('span', 'msg_date').text
            api_code = bs4.find('span', 'icon_apikey')['title']
            resources_data = {}
            for resource in resources_list.find_all('li'):
                resource_name = resource.find('div')['class']
                resource_name.remove('resourceIcon')
                resources_data[resource_name[0]] = int(resource['title'].replace('.', ''))

            def get_tech_and_quantity(tech_type):
                tech_list = bs4.find('ul', {'data-type': tech_type})
                for tech in tech_list.find_all('li', {'class': 'detail_list_el'}):
                    tech_id = int(re.search(r'([0-9]+)', tech.find('img')['class'][0]).group(1))
                    tech_amount = int(tech.find('span', 'fright').text.replace('.', ''))
                    yield (tech_id, tech_amount)

            spied_data = {'ships': {}, 'defense': {}, 'buildings': {}, 'research': {}}
            const_data = {
                'ships': [const.ships.ship_name, 'shipyard'],
                'defense': [const.buildings.defense_name, 'defenses'],
                'buildings': [const.buildings.building_name, None],
                'research': [const.research.research_name, 'research']
            }
            for tech_type in spied_data.keys():
                for tech_id, tech_amount in get_tech_and_quantity(tech_type):
                    if tech_type == 'ships' and tech_id in [212, 217]:
                            tech_name = const.buildings.building_name(
                                (tech_id, None, None)
                            )
                    else:
                        tech_name = const_data[tech_type][0](
                            (tech_id, None, const_data[tech_type][1])
                        )
                    spied_data[tech_type].update({tech_name: tech_amount})

            class Report:
                name = planet_coords.group(1)
                position = const.convert_to_coordinates(planet_coords.group(2))
                moon = bs4.find('figure', 'moon') is not None
                datetime = report_datetime
                metal = resources_data['metal']
                crystal = resources_data['crystal']
                deuterium = resources_data['deuterium']
                resources = [metal, crystal, deuterium]
                fleet = spied_data['ships']
                defenses = spied_data['defense']
                buildings = spied_data['buildings']
                research = spied_data['research']
                api = re.search(r'value=\'(.+?)\'', api_code).group(1)
                list = [
                    name, position, moon, datetime, metal,
                    crystal, deuterium, resources, fleet,
                    defenses, buildings, research, api
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

    def deconstruct(self, what, id):
        type = what[0]
        component = what[2]
        cant_deconstruct = [34, 33, 36, 41, 212, 217]
        if component not in ['supplies', 'facilities'] or type in cant_deconstruct:
            return
        response = self.session.get(
            url=self.index_php +
                'page=ingame&component={}&cp={}'
                .format(component, id)
        ).text
        deconstruct_token = re.search(
            r"var downgradeEndpoint = (.*)token=(.*)\&",
            response
        ).group(2)
        self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': component,
                    'modus': 3,
                    'token': deconstruct_token,
                    'type': type}
        )

    def cancel_building(self, id):
        self.cancel('building', id)

    def cancel_research(self, id):
        self.cancel('research', id)

    def cancel(self, what_queue, id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=overview',
            params={'cp': id}
        ).text
        cancel_token = re.search(
            rf"var cancelLink{what_queue} = (.*)token=(.*)\&",
            response
        ).group(2)
        parameters = re.search(
            rf"\"cancel{what_queue}\((.*)\, (.*)\,",
            response
        )
        if parameters is None:
            return
        self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'overview',
                    'modus': 2,
                    'token': cancel_token,
                    'action': 'cancel',
                    'type': parameters.group(1),
                    'listid': parameters.group(2)}
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
    
    def buy_offer_of_the_day(self):
    response = self.session.get(
        url=self.index_php +
            'page=ingame&component=traderOverview').text

    time.sleep(random.randint(250, 1500)/1000)

    response2 = self.session.post(
        url=self.index_php +
            'page=ajax&component=traderimportexport',
        data={
            'show': 'importexport',
            'ajax': 1
        },
        headers={'X-Requested-With': 'XMLHttpRequest'}).text

    time.sleep(random.randint(250, 1500) / 1000)

    bs4 = BeautifulSoup4(response2)

    try:
        item_available = bs4.find_partial(class_='bargain import_bargain take hidden').text
        return f'You have already accepted this offer!'
    except Exception as e:
        err = e
    try:
        item_price = bs4.find_partial(class_='price js_import_price').text
        item_price = int(item_price.replace('.', ''))
    except Exception as e:
        return f'err: {e}, failed to extract offer of the day price'

    try:
        planet_resources = re.search(r'var planetResources\s?=\s?({[^;]*});', response2).group(1)
        planet_resources = json.loads(planet_resources)
    except Exception as e:
        return f'err: {e}, failed to extract offer of the day planet resources'

    try:
        import_token = re.search(r'var importToken\s?=\s?"([^"]*)";', response2).group(1)
    except Exception as e:
        return f'err: {e}, failed to extract offer of the day import_token'

    try:
        multiplier = re.search(r'var multiplier\s?=\s?({[^;]*});', response2).group(1)
        multiplier = json.loads(multiplier)
    except Exception as e:
        return f'err: {e}, failed to extract offer of the day multiplier'

    form_data = {'action': 'trade'}

    remaining = item_price

    for celestial in list(planet_resources.keys()):
        metal_needed = int(planet_resources[celestial]['input']['metal'])
        if remaining < metal_needed * float(multiplier['metal']):
            metal_needed = math.ceil(remaining / float(multiplier['metal']))

        remaining -= metal_needed * float(multiplier['metal'])

        crystal_needed = int(planet_resources[celestial]['input']['crystal'])
        if remaining < crystal_needed * float(multiplier['crystal']):
            crystal_needed = math.ceil(remaining / float(multiplier['crystal']))

        remaining -= crystal_needed * float(multiplier['crystal'])

        deuterium_needed = int(planet_resources[celestial]['input']['deuterium'])
        if remaining < deuterium_needed * float(multiplier['deuterium']):
            deuterium_needed = math.ceil(remaining / float(multiplier['deuterium']))

        remaining -= deuterium_needed * float(multiplier['deuterium'])

        form_data.update(
            {
                'bid[planets][{}][metal]'.format(str(celestial)): '{}'.format(int(metal_needed)),
                'bid[planets][{}][crystal]'.format(str(celestial)): '{}'.format(str(crystal_needed)),
                'bid[planets][{}][deuterium]'.format(str(celestial)): '{}'.format(str(deuterium_needed)),
            }
        )

    form_data.update(
        {
            'bid[honor]': '0',
            'token': '{}'.format(import_token),
            'ajax': '1'
        }
    )

    time.sleep(random.randint(1500, 3000) / 1000)

    response3 = self.session.post(
        url=self.index_php +
            'page=ajax&component=traderimportexport&ajax=1&action=trade&asJson=1',
        data=form_data,
        headers={'X-Requested-With': 'XMLHttpRequest'}).json()

    try:
        new_token = response3['newAjaxToken']
    except Exception as e:
        return f'err: {e}, failed to extract offer of the day newAjaxToken'

    form_data2 = {
        'action': 'takeItem',
        'token': '{}'.format(new_token),
        'ajax': '1'
    }

    time.sleep(random.randint(250, 1500) / 1000)

    response4 = self.session.post(
        url=self.index_php +
            'page=ajax&component=traderimportexport&ajax=1&action=takeItem&asJson=1',
        data=form_data2,
        headers={'X-Requested-With': 'XMLHttpRequest'}).json()

    getitem = False
    if not response4['error']:
        getitem = True
    return getitem


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
