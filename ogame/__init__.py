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
                    '(KHTML, like Gecko) Chrome/100.0.4324.182 Safari/537.36'
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

    def highscore(self, page=1):
        data = {
            'page': 'highscoreContent',
            'category': '1',
            'type': '0',
            'site': str(page)
        }
        response = self.session.post(
            url=self.index_php,
            params=data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        bs4 = BeautifulSoup4(response.content)
        player_list = []
        for i in range(1, 101):
            rawy = bs4.select('tr', attrs={'class': ''})[i]
            class PlayerData:
                name = rawy.find('span', attrs={'class': 'playername'}).text.strip()
                player_id = int(rawy['id'].replace("position", ""))
                rank = int(rawy.find('td', attrs={'class': 'position'}).text.strip())
                points = int(rawy.find('td', attrs={'class': 'score'}).text.strip().replace(".", "").replace(",", ""))
                list = [
                    name, player_id, rank, points
                ]
            player_list.append(PlayerData)
        return player_list

    def character_class(self):
        character = self.landing_page.find_partial(
            class_='sprite characterclass medium')
        return character['class'][3]

    def lf_character_class(self, planet_id):
        response_class = self.session.get(
            url=self.index_php + 'page=ingame&component=overview',
            params={'cp': planet_id}
        ).text
        response_class = BeautifulSoup4(response_class)
        lf_character_class = response_class.find_partial(
            class_='lifeform-item-icon small')
        return lf_character_class['class'][2]

    def choose_character_class(self, classid):
        character = self.landing_page.find_partial(
            class_='sprite characterclass medium')
        data = {
            'page': "ingame",
            'component': "characterclassselection",
            'characterClassId': classid,
            'action': "selectClass",
            'ajax': '1',
            'asJson': '1'
        }
        if character['class'][3] == 'none':
            response = self.session.post(
                url=self.index_php,
                params=data,
                headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
            if response['status'] == 'success':
                return True
        return False

    def rank(self):
        rank = self.landing_page.find(id='bar')
        rank = rank.find_all('li')[1].text
        rank = re.search(r'\((.*)\)', rank).group(1)
        return int(rank)

    def shop_items(self):
        raw = self.landing_page.find('head')
        item_list = re.search(r'var itemNames = (.*);', str(raw)).group(1)
        json_list = json.loads(item_list)
        listofelems = [[value, key] for key, value in json_list.items()]
        item_duration = [" 7d", " 30d", " 90d"]
        for count, elem in enumerate(listofelems):
            index = max(count - 1, 0)
            if 87 > count > 1:
                if elem[0] == listofelems[index][0]:
                    if item_duration[0] in listofelems[max(index - 1, 0)][0]:
                        listofelems[index][0] = elem[0] + item_duration[1]
                    else:
                        listofelems[index][0] = elem[0] + item_duration[0]
                else:
                    if listofelems[index][0][:9] == listofelems[max(index - 1, 0)][0][:9]:
                        listofelems[index][0] = listofelems[index][0] + item_duration[2]
        return listofelems

    def buy_item(self, id, activate_it=False):
        response = self.session.get(
            url=self.index_php + 'page=shop&ajax=1&type={}'.format(id),
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )).text
        if activate_it:
            activateToken = re.search(r'activateToken="(.*)";', str(response)).group(1)
            response2 = self.session.post(
                url=self.index_php + 'page=inventory',
                data={'ajax': 1,
                      'token': activateToken,
                      'referrerPage': "ingame",
                      'buyAndActivate': id},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
        else:
            buyToken = re.search(r'var token="(.*)";v', str(response)).group(1)
            response2 = self.session.post(
                url=self.index_php + 'page=buyitem&item={}'.format(id),
                data={'ajax': 1,
                      'token': buyToken},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
        list = []
        if not response2['error']:
            if activate_it:
                item_data = response2['message']['item']
            else:
                item_data = response2['item']
            class Item:
                name = item_data['name']
                costs = int(item_data['costs'])
                duration = int(item_data['duration'])
                effect = item_data['effect']
                amount = int(item_data['amount'])
                list = [
                    name, costs, duration, effect, amount
                ]
            return Item
        else:
            return False

    def activate_item(self, id):
        response = self.session.get(
            url=self.index_php + 'page=shop&ajax=1&type={}'.format(id),
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).text
        activateToken = re.search(r'var token="(.*)";v', str(response)).group(1)
        response2 = self.session.post(
            url=self.index_php + 'page=inventory&item={}&ajax=1'.format(id),
            data={'ajax': 1,
                  'token': activateToken,
                  'referrerPage': "shop"},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        list = []
        if not response2['error']:
            item_data = response2['message']['item']
            class Item:
                name = item_data['name']
                costs = int(item_data['costs'])
                duration = int(item_data['duration'])
                effect = item_data['effect']
                canbeused = bool(item_data['canBeActivated'])
                amount = int(item_data['amount'])
                list = [
                    name, costs, duration, effect, canbeused, amount
                ]
            return Item
        else:
            return False

    def planet_ids(self):
        ids = []
        for celestial in self.landing_page.find_all(class_='smallplanet'):
            ids.append(int(celestial['id'].replace('planet-', '')))
        return ids

    def planet_names(self):
        return [planet.text for planet in
                self.landing_page.find_all(class_='planet-name')]

    def planet_coords(self):
        coords_list = [
            re.search(r'(.*?) (\[(.*?)])', cords.text).group(2)
            for cords in self.landing_page.find_all(class_='smallplanet')
        ]
        coords_list = [
            const.convert_to_coordinates(cords) + [1]
            for cords in coords_list
        ]
        return coords_list

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

    def moon_coords(self):
        coords_list = [
            re.search(r'(.*?) (\[(.*?)])', cords['title']).group(2)
            for cords in self.landing_page.find_all(class_='moonlink')
        ]
        coords_list = [
            const.convert_to_coordinates(cords) + [3]
            for cords in coords_list
        ]
        return coords_list

    def id_by_moon_name(self, name):
        for moon_name, id in zip(
                OGame.moon_names(self), OGame.moon_ids(self)
        ):
            if moon_name == name:
                return id

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

    def planet_infos(self):
        infos = []
        for planet in self.landing_page.find_all(class_='planetlink'):
            class Celestial:
                coordinates = re.search(r'\[(.*)]', planet['title']).group(1)
                coordinates = [int(coords) for coords in coordinates.split(':')]
                coordinates.append(const.destination.planet)
                diameter = re.search(r'br>(.*)km', planet['title']).group(1)
                diameter = int("".join(re.split('\\.|\\,', diameter)))
                total = int(re.search(r'\((.*)\/(.*)\)', planet['title']).group(2))
                if "overmark" in re.search(r'\((.*)\/(.*)\)', planet['title']).group(1):
                    used = total
                else:
                    used = int(re.search(r'\((.*)\/(.*)\)', planet['title']).group(1))
                free = total - used
                temperature = [
                    int(re.search(r'([0-9]+)°.* ([0-9]+)°', planet['title']).group(1)),
                    int(re.search(r'([0-9]+)°.* ([0-9]+)°', planet['title']).group(2))
                ]
            infos.append(Celestial)
        return infos

    def moon_infos(self):
        infos = []
        for moon in self.landing_page.find_all(class_='moonlink'):
            class Celestial:
                coordinates = re.search(r'\[(.*)]', moon['title']).group(1)
                coordinates = [int(coords) for coords in coordinates.split(':')]
                coordinates.append(const.destination.moon)
                diameter = re.search(r'br>(.*)km', moon['title']).group(1)
                diameter = int("".join(re.split('\\.|\\,', diameter)))
                total = int(re.search(r'\((.*)\/(.*)\)', moon['title']).group(2))
                if "overmark" in re.search(r'\((.*)\/(.*)\)', moon['title']).group(1):
                    used = total
                else:
                    used = int(re.search(r'\((.*)\/(.*)\)', moon['title']).group(1))
                free = total - used
            infos.append(Celestial)
        return infos

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
        textContent7 = re.search(
            r'textContent\[7] = "(.*)>(.*?) \(Place (.*?) (.*)<',
            response
        )
        class Celestial:
            diameter = int(textContent1.group(1).replace('.', '').replace(',', ''))
            used = int(textContent1.group(2))
            total = int(textContent1.group(4))
            free = total - used
            temperature = [
                textContent3[0],
                textContent3[1]
            ]
            coordinates = OGame.celestial_coordinates(self, id)
            points = int(textContent7.group(2).replace(".", "").replace(',', ''))
            rank = int(textContent7.group(3).replace(".", "").replace(',', ''))
        return Celestial

    def celestial_queue(self, id, name_list=False):
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
        shipyard_queue = None
        shipyard_time = re.search(r'var restTimeship2 = ([0-9]+)', response)
        if shipyard_time is None:
            shipyard_time = datetime.fromtimestamp(0)
        else:
            shipyard_time = int(shipyard_time.group(1))
            shipyard_time = datetime.now() + timedelta(seconds=shipyard_time)
            shipyard_queue = self.shipyard_queue(id, response, name_list)

        class Queue:
            research = research_time
            buildings = build_time
            shipyard = shipyard_time
            squeue = shipyard_queue
            list = [
                research,
                buildings,
                shipyard
            ]
        return Queue

    def shipyard_queue(self, id, input_response=False, name_list=False):
        if input_response:
            response = input_response
        else:
            response = self.session.get(
                url=self.index_php + 'page=ingame&component=overview',
                params={'cp': id}
            ).text

        bs4 = BeautifulSoup4(response)
        box_data = bs4.find(id='productionboxshipyardcomponent')
        queue = box_data.find_all(class_='tooltip js_hideTipOnMobile')

        if not queue and box_data.find(class_="queuePic"):
            add_sum = str(box_data.find(class_="shipSumCount").text)
            add_sum = ">" + add_sum + "</div>"
            new_response = str(box_data.find(class_="queuePic"))
            new_response = new_response.replace("img alt", "div title")
            new_response = new_response.replace("/>", add_sum)
            queue = queue + [BeautifulSoup(new_response, "lxml")]

        if not name_list:
            name_list = self.tooltip_names_import()

        amount = [0] * 27
        for tooltip in queue:
            if tooltip.find(class_="queuePic"):
                sname = tooltip.find(class_="queuePic")['title']
                samount = tooltip.text.replace("\n","").strip()
                if sname in name_list:
                    tindex = name_list.index(sname)
                    amount[tindex] += int(samount.replace(".", "").replace(",", ""))

        class Shipyard:
            def __init__(self, i):
                self.amount = amount[i]
                if amount[i] != 0:
                    self.in_construction = True
                else:
                    self.in_construction = False
                self.in_queue = amount[i]

        ShipsQueue = self.shi_class(Shipyard)
        ShipsQueue.solarSatellite = Shipyard(15)
        ShipsQueue.crawler = Shipyard(16)
        amount = amount[17:]
        DeffQueue = self.deff_class(Shipyard)
        Queue = self.merge_class(ShipsQueue, DeffQueue)
        del ShipsQueue, DeffQueue
        return Queue

    def deff_class(self, DeffClass):
        class Deff(object):
            rocket_launcher = DeffClass(0)
            laser_cannon_light = DeffClass(1)
            laser_cannon_heavy = DeffClass(2)
            gauss_cannon = DeffClass(3)
            ion_cannon = DeffClass(4)
            plasma_cannon = DeffClass(5)
            shield_dome_small = DeffClass(6)
            shield_dome_large = DeffClass(7)
            missile_interceptor = DeffClass(8)
            missile_interplanetary = DeffClass(9)

        return Deff

    def shi_class(self, ShipClass):
        class Ships(object):
            light_fighter = ShipClass(0)
            heavy_fighter = ShipClass(1)
            cruiser = ShipClass(2)
            battleship = ShipClass(3)
            interceptor = ShipClass(4)
            bomber = ShipClass(5)
            destroyer = ShipClass(6)
            deathstar = ShipClass(7)
            reaper = ShipClass(8)
            explorer = ShipClass(9)
            small_transporter = ShipClass(10)
            large_transporter = ShipClass(11)
            colonyShip = ShipClass(12)
            recycler = ShipClass(13)
            espionage_probe = ShipClass(14)

        return Ships

    def merge_class(self, ob1, ob2):
        my_dict = {**ob1.__dict__, **ob2.__dict__}
        del my_dict['__dict__'], my_dict['__weakref__'], my_dict['__doc__']

        class mergeClass(object):
            def __init__(self, my_dict):
                for key in my_dict:
                    setattr(self, key, my_dict[key])

        return mergeClass(my_dict)

    def tooltip_names_import(self):
        import inspect, os.path

        path = inspect.getframeinfo(inspect.currentframe()).filename
        tooltip_path = path.replace("__init__", "tooltip_names")

        infos_available = False
        if not os.path.exists(tooltip_path):
            w_file = open(tooltip_path, 'w')
            if w_file.write("import re") > 0:
                w_file.close()
        if os.path.exists(tooltip_path):
            r_file = open(tooltip_path, 'r'); r_data = r_file.readlines(); r_file.close()
            if r_data is not None:
                if "class " + str(self.language) + "_tooltips:\n" in r_data:
                    infos_available = True

        def ship_names(self):
            response = self.session.get(
                self.index_php + 'page=ingame&component=shipyard'
            ).text
            bs4 = BeautifulSoup4(response)
            snames = [
                status['aria-label']
                for status in bs4.find_all('li', {'class': 'technology'})
            ]
            return snames

        def defence_names(self):
            response = self.session.get(
                self.index_php + 'page=ingame&component=defenses'
            ).text
            bs4 = BeautifulSoup4(response)
            dnames = [
                status['aria-label']
                for status in bs4.find_all('li', {'class': 'technology'})
            ]
            return dnames

        if infos_available:
            import importlib
            def_name = str(self.language) + "_tooltips"
            tooltip = getattr(importlib.import_module('ogame.tooltip_names', __name__), def_name)
            return tooltip.list
        else:
            import_ships = ship_names(self)
            import_defense = defence_names(self)
            imported_data = import_ships + import_defense
            w_text = ["\n\n\nclass " + str(self.language) + "_tooltips:",
                      "list = ["]
            for i, names in enumerate(imported_data):
                text = "'" + names + "',"
                if i+1 == len(imported_data):
                    text = text.replace(",","")
                w_text.append(text)
            w_text.append("]")
            w_file = open(tooltip_path, 'a')
            if w_file.write("\n    ".join(w_text)) > 0:
                w_file.close()
            return imported_data

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
            return int(float(string.replace('.', '').replace(',', '')
                                   .replace('M', '000').replace('n', '')))

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
                attrs={'class': 'summary'}
            ).find_all(
                'td',
                attrs={'class': 'undermark'}
            )
            day_production = [
                to_int(day_production[0].span['title']),
                to_int(day_production[1].span['title']),
                to_int(day_production[2].span['title'])
            ]
            storage = bs4.find_all('tr')
            for stor in storage:
                if len(stor.find_all('td', attrs={'class': 'left2'})) != 0:
                    storage = stor.find_all('td', attrs={'class': 'left2'})
                    break
            storage = [to_int(store.span['title']) for store in storage]
            darkmatter = to_int(bs4.find(id='resources_darkmatter')['data-raw'])
            energy = to_int(bs4.find(id='resources_energy')['data-raw'])
            population = to_int(bs4.find(id='resources_population')['data-raw'])
            food = to_int(bs4.find(id='resources_food')['data-raw'])
        return Resources

    def resources_settings(self, id, settings=None):
        response = self.session.get(
            self.index_php + 'page=resourceSettings&cp={}'.format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        settings_form = {
            'saveSettings': 1,
        }
        token = bs4.find('input', {'name': 'token'})['value']
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
            int(level['data-value'].replace(",", "").replace(".", ""))
            for level in bs4.find_all('span', {'data-value': True})
            if not re.search(r'stockAmount', str(level))
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
            solar_satellite = Supply(5)
            crawler = Supply(6)
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

    def lf_facilities(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=lfbuildings&cp={}'
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

        class LfFacilitie:
            def __init__(self, i):
                self.level = levels[i]
                self.is_possible = OGame.isPossible(technologyStatus[i])
                self.in_construction = OGame.inConstruction(technologyStatus[i])

        class LfFacilities(object):
            residential_sector = LfFacilitie(0)
            biosphere_farm = LfFacilitie(1)
            research_centre = LfFacilitie(2)
            academy_of_sciences = LfFacilitie(3)
            neuro_calibration_centre = LfFacilitie(4)
            high_energy_smelting = LfFacilitie(5)
            food_silo = LfFacilitie(6)
            fusion_powered_production = LfFacilitie(7)
            skyscraper = LfFacilitie(8)
            biotech_lab = LfFacilitie(9)
            metropolis = LfFacilitie(9)
            planetary_shield = LfFacilitie(10)

        return LfFacilities

    def moon_facilities(self, id):
        response = self.session.get(
            url='{}page=ingame&component=facilities&cp={}'
                .format(self.index_php, id)
        ).text
        bs4 = BeautifulSoup4(response)
        levels = [
            int(level['data-value'])
            for level in bs4.find_all(class_=['targetlevel', 'level'])
            if level.get('data-value') and level.get('class') == ['level']
        ]
        technologyStatus = [
            status['data-status']
            for status in bs4.find_all('li', {'class': 'technology'})
        ]
        moon_data = bs4.find(class_=r"smallplanet smaller hightlightMoon")
        if moon_data:
            moon_data = moon_data.find(class_="moonlink")['title']
        else:
            moon_data = bs4.find(class_="moonlink")['title']

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
            fields = [
                int(re.search(r'.\(([0-9]+)\/([0-9]+)\)', moon_data).group(ibm))
                for ibm in range(1, 3)
            ]

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
        print(f'DEBUG technology_status {technology_status}')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on')+technology_status.count('disabled')-1:
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
        print(f'DEBUG technology_status {technology_status}')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on')+technology_status.count('disabled')-1:
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
        print(f'DEBUG technology_status {technology_status}')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on')+technology_status.count('disabled')-1:
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
        print(f'DEBUG technology_status {technology_status}')

        class LfResearch:
            def __init__(self, i):
                if i <= technology_status.count('on')+technology_status.count('disabled')-1:
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

        return LfResearches

    def ships(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=shipyard&cp={}'
            .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        ships_amount = [
            int(level['data-value'].replace(",","").replace(".",""))
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

        Ships = self.shi_class(Ship)
        Ships.crawler = Crawler
        Ships.res = self.add_resources(bs4)
        return Ships

    def defences(self, id):
        response = self.session.get(
            self.index_php + 'page=ingame&component=defenses&cp={}'
            .format(id)
        ).text
        bs4 = BeautifulSoup4(response)
        defences_amount = [
            int(level['data-value'].replace(",","").replace(".",""))
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

        Defences = self.deff_class(Defence)
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

        debris_fields = []
        debris_rows = bs4.find_all('td', {'class': 'debris'})
        for row in debris_rows:
            has_debris = True
            row['class'].remove('debris')
            if 'js_no_action' in row['class']:
                has_debris = False
                row['class'].remove('js_no_action')
            debris_cord = int(row['class'][0].replace('js_debris', ''))
            debris_cord = const.coordinates(
                coords[0],
                coords[1],
                int(debris_cord), const.destination.debris
            )
            debris_resources = [0, 0, 0]
            if has_debris:
                debris_resources = row.find_all('li', {'class': 'debris-content'})
                debris_resources = [
                    int(debris_resources[0].text.split(':')[1].replace(',', '').replace('.', '')),
                    int(debris_resources[1].text.split(':')[1].replace(',', '').replace('.', '')),
                    0
                ]
            dlist = [
                debris_cord, has_debris, debris_resources
            ]
            debris_fields.append(dlist)

        planets = []
        for row in bs4.select('#galaxytable .row'):
            status = row['class']
            status.remove('row')
            if row.find('span', class_='status_abbr_outlaw'):
                status.append("outlaw_filter")
            if row.find('span', class_='status_abbr_admin'):
                status.append("admin_filter")
            if row.find('span', class_='status_abbr_banned'):
                status.append("banned_filter")
            if row.find('span', class_='status_abbr_honorableTarget'):
                status.append("honorableTarget_filter")
            if row.find('span', class_=['rank_bandit1', 'rank_bandit2', 'rank_bandit3']):
                status.append("bandit_filter")
            if row.find('span', class_=['rank_starlord1', 'rank_starlord2', 'rank_starlord3']):
                status.append("honorableTarget_filter")
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
            moon = moon_pos is not None

            alliance_id = row.find(rel=re.compile(r'alliance[0-9]+'))
            alliance_id = playerId(
                alliance_id['rel']) if alliance_id else None

            # find user activity on planet
            activity_tag = row.select('div[class*="activity"]')
            if len(activity_tag) != 0:
                if 'minute15' in activity_tag[0]['class']:
                    flag_activity = 15 # if minute15, set as 15
                elif 'showMinutes' in activity_tag[0]['class']:
                    flag_str = row.findAll(
                        "div", {"title": "Activity"})[0].string
                    # if showMinutes, set as real count
                    flag_activity = int(
                        re.search(r'[0-9]+', flag_str).group())
                else:
                    # set -1 if no activity
                    flag_activity = -1
            else:
                # set -2 if something failed
                flag_activity = -2

            debris_data = [planet_cord[:2] + [2], False, [0, 0, 0]]
            debris_index = None
            for list_index, debris_list in enumerate(debris_fields):
                if planet_cord[2] == debris_list[0][2]:
                    debris_index = list_index
            if debris_index:
                debris_data = debris_fields[debris_index]

            moon_size_row = 0
            if moon:
                moon_size_row = int(row.select_one("td.moon span#moonsize").text.split()[0])

            debris_16 = bs4.find(class_="expeditionDebrisSlotBox")
            if debris_16:
                debris_data = debris_16.find(class_='ListLinks').text.replace(".","")
                debris_16 = [int(data.replace(",","").replace(".","")) for data in re.findall(r'\d+', debris_data)]
            else:
                debris_16 = [0, 0, 0]   # [met, kris, pf]

            class Position:
                position = planet_cord
                planet_name = row.find(id=re.compile(r'planet[0-9]+')).h1.span.text
                player = player_name[pid]
                player_id = pid
                rank = player_rank.get(pid)
                status = planet_status
                moon = moon_pos is not None
                moon_size = moon_size_row
                alliance = alliance_name.get(alliance_id)
                debris_coord = debris_data[0]
                has_debris = debris_data[1]
                resources = debris_data[2]
                expedition_debris = debris_16[:2]
                needed_pf = debris_16[2]
                # add attribute for planet activity info
                activity = flag_activity
                list = [
                    position, planet_name, player, activity,
                    player_id, rank, status, moon, moon_size, alliance,
                    debris_coord, has_debris, resources, expedition_debris, needed_pf
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
                    int(debris_resources[0].text.split(':')[1].replace(',', '').replace('.', '')),
                    int(debris_resources[1].text.split(':')[1].replace(',', '').replace('.', '')),
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
                if coords.find(class_=Coords).a is not None  # optional
        ]
        coordinate = [
            const.convert_to_coordinates(coords)
            for coords in coordinate
        ]
        destin = Coords.replace("destCoords", "destFleet")\
                       .replace("coordsOrigin", "originFleet")\
                       .replace("destinationCoords", "destinationData")\
                       .replace("originCoords", "originData")                  # for hostile/friendly_fleets
        destination = [
            dest.find(class_=destin).find('figure', {'class': 'planetIcon'})
            if dest.find(class_=destin).find('figure', {'class': 'planetIcon'}) is not None
            else BeautifulSoup4('<figure class="planetIcon planet"></figure>').find("figure")
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

    def extra_slots(self):
        response = self.landing_page
        bs4 = BeautifulSoup4(str(response))
        active_items = bs4.find_all(class_="detail_button")
        expo_items = [
            '8c1f6c6849d1a5e4d9de6ae9bb1b861f6f7b5d4d', 'e54ecc0416d6e96b4165f24238b03a1b32c1df47',
            'a5784c685c0e1e6111d9c18aeaf80af2e0777ab4', '31a504be1195149a3bef05b9cc6e3af185d24ef2',
            'b2bc9789df7c1ef5e058f72d61380b696dde54e8', '4f6f941bbf2a8527b0424b3ad11014502d8f4fb8',
            'fd7d35e73d0e09e83e30812b738ef966ea9ef790', '9336b9f29d36e3f69b0619c9523d8bec5e09ab8e',
            '540410439514ac09363c5c47cf47117a8b8ae79a'
        ]
        fleet_items = [
            '94a28491b6fd85003f1cb151e88dde106f1d7596', '0684c6a5a42acbb3cd134913d421fc28dae6b90d',
            'bb47add58876240199a18ddacc2db07789be1934', 'c4e598a85805a7eb3ca70f9265cbd366fc4d2b0e',
            'f8fd610825fb4a442e27e4e9add74f050e040e27', 'a693c5ce3f5676efaaf0781d94234bea4f599d2e',
            '1808bf7639b81ac3ac87bcb7eb3bbba0a1874d0a', '5a8000c372cd079292a92d35d4ddba3c0f348d3b',
            '1f7024c4f6493f0c589e1b00c76e6ced258c00e5'
        ]
        xtra_slots = [0, 0]
        for item_type in active_items:
            add = int(re.search(r"br />\n\+(\d) ", item_type['title']).group(1))
            if item_type['ref'] in expo_items:
                xtra_slots[0] += add
            if item_type['ref'] in fleet_items:
                xtra_slots[1] += add
        return xtra_slots

    def slot_fleet(self):
        response = self.session.get(
            self.index_php + 'page=ingame&component=fleetdispatch'
        ).text
        bs4 = BeautifulSoup4(response)
        slots = bs4.find('div', attrs={'id': 'slots', 'class': 'fleft'})
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

    def friendly_fleet_data(self, names=None):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly'
                                 '&component=eventList&action=fetchEventBox&ajax=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).text
        bs4 = BeautifulSoup4(response)
        fleetDetails = bs4.find_all("span", class_='friendly')
        tooltip = [
            fleet.parent.parent.find(class_="tooltip")
            for fleet in fleetDetails
        ]
        tooltip_data = [
            self.fleet_tooltip(data, names)
            for data in tooltip
        ]
        return tooltip_data

    def fleet_tooltip(self, tooltip, ship_names=None):
        def aquire_shipnames(self):
            response = self.session.get(
                self.index_php + 'page=ingame&component=shipyard'
            ).text
            bs4 = BeautifulSoup4(response)
            names = [
                status['aria-label']
                for status in bs4.find_all('li', {'class': 'technology'})
            ]
            return names[:15]

        def pre_parse(table):
            dict = {
                '&lt;': '<',
                '&gt;': '>',
                '&quot;': '"',
                '&amp;': '&',
                '&nbsp;': '\u00A0',
                '\xa0': '\u00A0',
                "title=\'": 'title=""'
            }
            regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
            return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], str(table))

        if not ship_names or len(ship_names) < 15:
            ship_names = self.tooltip_names_import()[:15]
            if not ship_names:
                ship_names = aquire_shipnames(self)

        tooltip_data = BeautifulSoup4(pre_parse(tooltip)).find_all("td")  # , 'html5lib'
        data_set = 0
        ship_amount = []; ship_types = []; shipments = []
        for data in tooltip_data:
            if data.text != '\xa0':
                text = data.text.replace(":", "").replace(".", "").replace(",", "")
                if data_set < 1:
                    if text.isdigit():
                        ship_amount.append(int(text))
                    else:
                        ship_types.append(text)
                else:
                    if text.isdigit():
                        shipments.append(int(text))
            else:
                data_set += 1
        if not shipments:
            shipments = [0, 0, 0]
        amount = [0] * 15
        if ship_amount and ship_names and len(ship_amount) == len(ship_types):
            for ii, name in enumerate(ship_types):
                if name in ship_names:
                    index = [
                        ip for ip, xmb in enumerate(ship_names)
                        if name == xmb
                    ]
                    if index:
                        amount[index[0]] = max(ship_amount[ii], 0)

        class Ship:
            def __init__(self, i):
                self.amount = amount[i]

        class Ress:
            def __init__(self):
                self.resources = shipments
                self.metal = shipments[0]
                self.crystal = shipments[1]
                self.deuterium = shipments[2]

        Ships = self.shi_class(Ship)
        Ships.shipment = Ress()
        return Ships

    def hostile_fleet(self):
        if not self.attacked():
            return []
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList'
        ).text
        bs4 = BeautifulSoup4(response)

        eventFleet = bs4.find_all('span', class_='hostile')
        eventFleet = [
            child.parent.parent
            for child in eventFleet
            if child.parent.parent['id'][9:10] is not 'u'
        ]

        fleet_ids = [id['id'] for id in eventFleet]
        fleet_ids = [
            re.search('eventRow-(.*)', id).group(1)
            for id in fleet_ids
        ]

        mission_types = [
            int(event['data-mission-type'])
            for event in eventFleet
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
            int(id.find_all("td", class_='sendMail')[0].a['data-playerid'])
            for id in eventFleet
        ]
        player_names = [
            name.find_all("td", class_='sendMail')[0].a['title']
            for name in eventFleet
        ]

        fleets = []
        for i in range(len(fleet_ids)):
            class Fleets:
                id = fleet_ids[i]
                mission = mission_types[i]
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

    def jump_fleet(self, origin_id, target_id, ships):
        self.session.get(
            url='{}page=ingame&component=facilities&cp={}'
                 .format(self.index_php, origin_id)
        )

        response1 = self.session.get(self.index_php + 'page=jumpgatelayer')
        jump_token = re.search(r" value='(.*)'", response1.text).group(1)
        possible_dest = re.findall(r' value="(.*[0-9+])"', response1.text)
        if str(target_id) not in possible_dest:
            ready = re.search(r' <div id="(.*)"', response1.text)
            cooldown = re.search(r'\("#cooldown"\), (.*),', response1.text)
            if ready and cooldown:
                return int(cooldown.group(1))                            # returns cooldown time in seconds
            return False
        form_data = {'token': jump_token,
                     'zm': target_id}
        for ship in ships:
            ship_type = 'ship_{}'.format(ship[0])
            form_data.update({ship_type: ship[1]})

        response2 = self.session.post(
            url=self.index_php + 'page=jumpgate_execute&ajax=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

        if response2.json()['status']:
            return True
        else:
            return False

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

    def send_buddy(self, player_id, msg):
        response = self.session.get(
            url=self.index_php +
                f'page=ingame&component=buddies&action=7&id={player_id}&ajax=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).text
        chat_token = re.search("value='(.*)'", response).group(1)
        response = self.session.post(
            url=self.index_php,
            data={'page': 'ingame',
                  'component': 'buddies',
                  'action': 6,
                  'id': player_id,
                  'token': chat_token,
                  'text': msg},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        bs4 = BeautifulSoup4(response.text)
        content = bs4.find('div', class_="buddylistContent")
        if content.table:
            return True
        else:
            print(" ".join(content.text.split()))            # output 'You have already sent a request to this player.' / 'Invalid player.'
            return False

    def reward_system(self):
        bs4 = self.landing_page
        menue = bs4.find_all('span', class_='textlabel')
        if "Rewards" in [title.text for title in menue]:
            return True
        else:
            return False

    def rewards(self, tier=None, reward=None):
        def grab_token():
            response1 = self.session.get(
                url=self.index_php + f'page=ingame&component=rewarding&tab=rewards',
                headers={'X-Requested-With': 'XMLHttpRequest'})
            if response1.status_code != 200:
                return False
            return response1
        def reward_data(show_tier=tier):
            response1 = grab_token()
            if response1 is False:
                return False
            token = re.search('var token = "(.*)"', response1.text).group(1)
            response2 = self.session.get(
                url=self.index_php + 'page=ingame&component=rewarding&tab=rewards'
                                     '&action=fetchRewards&ajax=1'
                                     f'&tier={show_tier}&token={token}',
                headers={'X-Requested-With': 'XMLHttpRequest'})
            if response2.status_code != 200:
                return False
            item_names = re.findall(r'"rewardName\\">([^<\\]*)', response2.text)
            quantity = re.findall(r'"quantity\\">\\\D* ([^<\\]*)\\n', response2.text)
            item_ids = re.findall(r'data-id=\\"([0-9]+)', response2.text)
            tritium = re.findall(r'\\u([^ ]*)', response2.text)
            return [response2, item_names, quantity, item_ids, tritium]
        if tier and reward:
            data = reward_data()
            if data[0] is False or data[4][0] != data[4][1]:
                return False
            item = max(min(reward - 1, 2), 0)
            ajax_token = data[0].json()['newAjaxToken']
            reward_id = int(data[3][item])
            response3 = self.session.post(
                url=self.index_php + 'page=ingame&component=rewarding&tab=rewards'
                                     '&action=submitReward&asJson=1',
                data={'selectedReward': reward_id,
                      'selectedTier': tier,
                      'token': ajax_token},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            class selectedReward:
                status = response3.json()['status']
                name = data[1][item]
                amount = data[2][item].strip()
                id = data[3][item].strip()
            return selectedReward
        else:
            response = grab_token()
            if response is False:
                return False
            max_tier = int(re.findall(r'data-tier="([0-9])', response.text)[-1])
            progress = re.search(r'title=.*([0-9])\/([0-9])', response.text)
            item_list = []
            claimable_list = []
            for ipx in range(max_tier):
                data = reward_data(ipx+1)
                item_list.append([(data[1][i], data[2][i], data[3][i]) for i in range(3)])
                claimable_list.append(data[4][0] == data[4][1])
            class TierList:
                highest_tier = max_tier
                event_progress = [int(progress.group(1)), int(progress.group(2))]
                claimable = claimable_list
                rewards = item_list
                list = [highest_tier, event_progress, claimable, rewards]
            return TierList

    def get_messages(self):
        response = self.session.post(
            url=self.index_php + 'page=ajaxChat&action=showPlayerList',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        chats_ = int(re.search('countOfChats":(\d+)', response.text).group(1))
        if not bool(chats_):
            return []
        content = response.json()['listOfChats']
        chat_ids = [id_s for id_s in content]
        messages = [content[ids] for ids in chat_ids]
        message_data = []
        time_f = "%Y-%m-%d %H:%M:%S"; time_ff = "%H:%M:%S-%d.%m.%Y"
        for data in messages:
            chat_history = []
            if data['unreadCounter'] >= 1:
                response2 = self.session.post(url=self.index_php + 'page=ajaxChat',
                                      data={'playerId': int(data['partnerId']), 'mode': 2,
                                            'ajax': 1, 'updateUnread': 1},
                                      headers={'X-Requested-With': 'XMLHttpRequest'})  # read message/mark as read
                chat_data = response2.json()['data']
                chat_overview = response2.json()['chatItems']
                authors_list = re.findall(r'w">\n (.*)</', chat_data)
                authors = [author.strip() for author in authors_list][-10:]
                messages = [chat['chatContent'] for chat in chat_overview][-10:]
                chat_history = [[authors[count], message]
                                for count, message in enumerate(messages)]
            class Message:
                player = data['partnerName']
                player_id = data['partnerId']
                status = data['unreadCounter']
                text = data['text']
                time = datetime.strptime(data['time'], time_f).strftime(time_ff)
                alliance = data['allianceName']
                rank = data['highscorePosition']
                chat = chat_history
                list = [
                    player, player_id, status, text,
                    time, alliance, rank, chat
                ]
            message_data.append(Message)
        return message_data

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
            url=self.index_php +
                'page=ingame&component=overview&action=confirmPlanetGiveup&ajax=1&asJson=1',
            data={
                'abandon': code_abandon,
                'token': token_abandon,
                'password': self.password,
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        new_token = None
        if response.get("password_checked") and response["password_checked"]:
            new_token = response["newAjaxToken"]
        if new_token:
            self.session.post(
                url=self.index_php +
                    'page=ingame&component=overview&action=planetGiveup&ajax=1&asJson=1',
                data={
                    'abandon': code_abandon,
                    'token': new_token,
                    'password': self.password,
                },
            headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
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
                # return None if level of espionage too low to retrieve information
                if "unable" in tech_list.text:
                    yield(None, None)
                else:
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
                    if tech_id is None:
                        spied_data[tech_type] = "detail_list_fail" # replace dict with message string
                        break
                    elif tech_type == 'ships' and tech_id in [212, 217]:
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

    def get_page_messages(self, page, tab_id):
        payload = {
                "messageId": "-1",
                "tab": '{}'.format(tab_id),
                "action": "107",
                "pagination": '{}'.format(page),
                "ajax": "1",
        }

        return self.session.get(url=self.index_php + 'page=messages', params=payload)

    def extract_other_message(self, response):
        msgs = []
        bs4 = BeautifulSoup4(response.text)
        nb_page = bs4.select("ul.pagination li.paginator")[-1].attrs['data-page']
        msgs_raw = bs4.select("li.msg")
        msg_id = 0
        message_date = 'False'
        message_sender = 'False'
        message_text = 'False'
        for msg_raw in msgs_raw:
            if 'data-msg-id' in str(msg_raw):
                msg_id = msg_raw['data-msg-id']
                msgs.append(msg_id)
            else:
                continue
            if 'msg_date' in str(msg_raw):
                message_date = str(msg_raw.select_one("li.msg div.msg_head span.fright span.msg_date").text)
                msgs.append(message_date)
            if 'msg_sender' in str(msg_raw):
                message_sender = str(msg_raw.select_one("li.msg div.msg_head span.msg_sender").text)
                msgs.append(message_sender)
            if 'msg_content' in str(msg_raw):
                message_text = str(msg_raw.select_one("li.msg span.msg_content").text.strip())
                msgs.append(message_text)

        return msgs, nb_page

    def get_other_messages(self):
        tab_id = 24
        page = 1
        nb_page = 1
        msgs = []
        new_messages_counter = self.get_new_messages_count()
        print(f"New other messages: {new_messages_counter[4]}")
        while int(page) <= int(nb_page):
            response = self.get_page_messages(page, tab_id)
            new_messages, new_nb_page = self.extract_other_message(response)
            msgs.append(new_messages)
            nb_page = new_nb_page
            page += 1

        return msgs

    def extract_combat_summary_reports_message(self, response):
        msgs = []
        bs4 = BeautifulSoup4(response.text)
        nb_page = bs4.select("ul.pagination li.paginator")[-1].attrs['data-page']
        msgs_raw = bs4.select("li.msg")
        for msg_raw in msgs_raw:
            if 'data-msg-id' in str(msg_raw):
                msg_id = msg_raw['data-msg-id']
            else:
                continue

            message_destination = str(msg_raw.select_one("div.msg_head a").text)
            message_destination = const.convert_to_coordinates(message_destination)

            fleet_lost_first_round_message = False
            if 'planet' in str(msg_raw.select_one("div.msg_head figure")):
                message_destination_type = 1
            elif 'moon' in str(msg_raw.select_one("div.msg_head figure")):
                message_destination_type = 3
            else:
                message_destination_type = 1
                fleet_lost_first_round_message = True
            message_destination = const.coordinates(int(message_destination[0]), int(message_destination[1]),
                                                    int(message_destination[2]), int(message_destination_type))

            if not fleet_lost_first_round_message:
                res_title = msg_raw.select("span.msg_content div.combatLeftSide span")[1].attrs['title']
                re_res = re.search('([\\d.,]+)<br/>[^\\d]*([\\d.,]+)<br/>[^\\d]*([\\d.,]+)', res_title)
                re_res = const.resources(re_res[1], re_res[2], re_res[3])

                debris_field_title = msg_raw.select("span.msg_content div.combatLeftSide span")[2].attrs['title']

                res_text = msg_raw.select("span.msg_content div.combatLeftSide span")[1]
                re_res_text = re.search('[\\d.,]+[^\\d]*([\\d.,]+)', str(res_text))
                re_res_text = re_res_text[1]

                message_date = str(msg_raw.select_one("span.msg_date").text)

                message_text = msg_raw.select("li.msg span.msg_content span.msg_ctn")

                attacker_name_message = message_text[0].text
                attacker_name_message = attacker_name_message[
                                        attacker_name_message.find("(") + 1:attacker_name_message.find(")")]

                attacker_point_lost_message = message_text[0].text
                attacker_point_lost_message = attacker_point_lost_message[
                                              attacker_point_lost_message.find(attacker_name_message) + len(
                                                  attacker_name_message) + 3:]

                defender_name_message = message_text[3].text
                defender_name_message = defender_name_message[
                                            defender_name_message.find("(") + 1:defender_name_message.find(")")]

                defender_point_lost_message = message_text[3].text
                defender_point_lost_message = defender_point_lost_message[
                                              defender_point_lost_message.find(defender_name_message) + len(
                                                  defender_name_message) + 3:]

                repaired_message = message_text[4].text
                repaired_message = repaired_message[
                                   repaired_message.find(":") + 1:]

                try:
                    moon_chance_message = message_text[5].text
                    moon_chance_message = moon_chance_message[
                                          moon_chance_message.find(":") + 1:moon_chance_message.find("%")]
                except:
                    moon_chance_message = None

                # monn_created_message = # ToDo Find color green?....

                link = str(msg_raw.select_one("div.msg_actions a span.icon_attack").parent)
                link = link.replace("&amp;", "&")
                re_link = re.search('galaxy=(\\d+)&system=(\\d+)&position=(\\d+)&type=(\\d+)&', str(link))
                re_link = const.coordinates(int(re_link[1]), int(re_link[2]), int(re_link[3]), int(re_link[4]))

                if re_link == message_destination:
                    re_link = None
                    attacker_name_message = 'Self'
            else:
                re_res = False
                debris_field_title = False
                re_res_text = False
                message_date = False
                re_link = False
                attacker_name_message = False
                attacker_point_lost_message = False
                defender_name_message = False
                defender_point_lost_message = False
                repaired_message = False
                moon_chance_message = False

            class CombatReportSummary:
                id = msg_id
                destination = message_destination
                fleet_lost_first_round = fleet_lost_first_round_message
                resources = re_res
                df = debris_field_title
                loot = re_res_text
                created_at = message_date
                origin = re_link
                attacker_name = attacker_name_message
                attacker_lost = attacker_point_lost_message
                defender_name = defender_name_message
                defender_lost = defender_point_lost_message
                repaired = repaired_message
                moon_chance = moon_chance_message
                list = [
                    id, destination, fleet_lost_first_round, resources, df, loot, created_at,
                    origin, attacker_name, attacker_lost, defender_name,
                    defender_lost, repaired, moon_chance
                ]

            msgs.append(CombatReportSummary)
        return msgs, nb_page

    def get_new_messages_count(self):
        payload = {
            "tab": '2',
            "ajax": "1",
        }

        response = self.session.get(url=self.index_php + 'page=messages', params=payload).text
        bs4 = BeautifulSoup4(response)
        msgs_raw = bs4.select("ul li")
        new_messages = []
        i = 0
        for raw in msgs_raw:
            if i < 5:
                raw = raw.text.strip()
                if raw.find("(") > 0:
                    raw = int(raw[raw.find("(") + 1:raw.find(")")])
                else:
                    raw = 0
                new_messages.append(raw)
            i += 1
        return new_messages  # [espionage, combat reports, expeditions, unions/transport, other]

    def get_combat_reports_messages(self):
        tab_id = 21
        page = 1
        nb_page = 1
        msgs = []
        new_messages_counter = self.get_new_messages_count()
        print(f"New Combatreports: {new_messages_counter[1]}")
        while int(page) <= int(nb_page):
            response = self.get_page_messages(page, tab_id)
            new_messages, new_nb_page = self.extract_combat_summary_reports_message(response)
            msgs.append(new_messages)
            nb_page = new_nb_page
            page += 1

        return msgs

    def get_delete_messages_token(self):
        payload = {
            "tab": '20',
            "ajax": "1",
        }
        page_html = self.session.get(url=self.index_php + 'page=messages', params=payload).text
        try:
            regex = r"name='token' value='([^']+)'"
            token = re.search(regex, page_html, re.MULTILINE).group(1)
            return token
        except Exception as e:
            print(f'token not found. {e} ')
            return False

    def delete_all_message_from_tab(self, tab_id):
        # tabid: 20 = > Espionage
        # tabid: 21 = > Combat
        # tabid: 22 = > Expeditions
        # tabid: 23 = > Unions / Transport
        # tabid: 24 = > Other
        token = self.get_delete_messages_token()

        payload = {
            "messageId": "-1",
            "tabid": '{}'.format(tab_id),
            "action": "103",
            "token": '{}'.format(token),
            "ajax": "1",
        }
        if token:
            self.session.post(url=self.index_php + 'page=messages', params=payload)
            return True
        else:
            print(f'error deleting messages')
            return False

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
        btype = what[0]
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
                    'type': btype,
                    'menge': amount}
        )

    def deconstruct(self, what, id):
        btype = what[0]
        component = what[2]
        cant_deconstruct = [33, 36, 41, 212, 217]
        if component not in ['supplies', 'facilities'] or btype in cant_deconstruct:
            return
        response = self.session.get(
            url=self.index_php +
                'page=ingame&component={}&cp={}'
                .format(component, id)
        ).text
        deconstruct_token = re.search(
            r"var downgradeEndpoint = (.*)token=(.*)&",
            response
        ).group(2)
        self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': component,
                    'modus': 3,
                    'token': deconstruct_token,
                    'type': btype}
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
            rf"var cancelLink{what_queue} = (.*)token=(.*)&",
            response
        ).group(2)
        parameters = re.search(
            rf"\"cancel{what_queue}\((.*), (.*),",
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

    def vacation_mode(self, activate=True):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=preferences'
                .format(id),
            headers={'X-Requested-With': 'XMLHttpRequest'})
        bs4 = BeautifulSoup4(response.text)
        vacation_mode = bs4.find("div", id="advice-bar").a
        deactivated_button = re.search(r'\s{12}disabled: (.*)', response.text)

        change_status = "off"
        if activate:
            change_status = "on"
        if vacation_mode:
            if activate:
                return True
            else:
                vacation_till = re.search('.* (.* .*).', vacation_mode['title']).group(1)
                return datetime.strptime(vacation_till, "%d.%m.%Y %H:%M:%S")
        if not vacation_mode and activate and deactivated_button.group(1) == 'true':
            return False

        activate_token = re.search("name='token' value='(.*)'", response.text).group(1)
        form_data = {'mode': 'save',
                     'selectedTab': 0,
                     'token': activate_token,
                     'db_character': '',
                     'spio_anz': 1,
                     'spySystemAutomaticQuantity': 1,
                     'spySystemTargetPlanetTypes': 0,
                     'spySystemTargetPlayerTypes': 0,
                     'spySystemIgnoreSpiedInLastXMinutes': 0,
                     'activateAutofocus': 'on',
                     'eventsShow': 1,
                     'settings_sort': 0,
                     'settings_order': 0,
                     'showDetailOverlay': 'on',
                     'animatedSliders': 'on',
                     'animatedOverview': 'on',
                     'msgResultsPerPage': 10,
                     'auctioneerNotifications': 'on',
                     'showActivityMinutes': 1,
                     'urlaubs_modus': change_status}
        if change_status == "off":
            form_data = {'mode': 'save',
                         'selectedTab': 0,
                         'token': activate_token,
                         'db_character': ''}
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=preferences',
            data=form_data)
        if response.status_code not in [200, 302]:
            return False
        else:
            return True

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
