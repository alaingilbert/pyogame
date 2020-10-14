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
    def __init__(self, universe, username, password, token=None, user_agent=None, proxy='', language=None):
        self.forOgameVersion = [7, 5, 1]
        self.universe = universe
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.proxy = proxy
        self.language = language
        self.session = requests.Session()
        self.session.proxies.update({'https': self.proxy})
        self.token = token
        if self.user_agent is None:
            self.user_agent = {
                'User-Agent':
                    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/83.0.4103.97 Mobile Safari/537.36'}
        self.session.headers.update(self.user_agent)

        if token is None:
            self.login()
        else:
            self.session.headers.update({'authorization': 'Bearer {}'.format(token)})
            if 'error' in self.session.get('https://lobby.ogame.gameforge.com/api/users/me/accounts').json():
                del self.session.headers['authorization']
                self.login()

        servers = self.session.get('https://lobby.ogame.gameforge.com/api/servers').json()
        for server in servers:
            if server['name'] == self.universe:
                self.server_number = server['number']
                break
            elif server['name'] == self.universe and self.language is None:
                self.server_number = server['number']
                break
        try:
            accounts = self.session.get('https://lobby.ogame.gameforge.com/api/users/me/accounts').json()
            self.accounts = accounts
            for account in accounts:
                if account['server']['number'] == self.server_number and account['server']['language'] == self.language:
                    self.server_id = account['id']
                    break
                elif account['server']['number'] == self.server_number and self.language is None:
                    self.server_id = account['id']
                    self.language = account['server']['language']
                    break
            self.index_php = 'https://s{}-{}.ogame.gameforge.com/game/index.php?'.format(self.server_number,
                                                                                         self.language)
        except AttributeError:
            raise Exception("Universe not found")

        login_link = self.session.get(
            url='https://lobby.ogame.gameforge.com/api/users/me/loginLink?',
            params={'id': self.server_id,
                    'server[language]': self.language,
                    'server[number]': self.server_number,
                    'clickedButton': 'account_list'}
        ).json()
        self.landing_page = self.session.get(login_link['url']).text
        self.landing_page_text = self.session.get(self.index_php + 'page=ingame').text
        self.landing_page = self.BS4(self.landing_page_text)

        self.player = self.landing_page.find('meta', {'name': 'ogame-planet-name'})['content']
        self.player_id = int(self.landing_page.find('meta', {'name': 'ogame-planet-id'})['content'])

    def BS4(self, response):
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

    def login(self):
        self.session.get('https://lobby.ogame.gameforge.com/')
        login_data = {'identity': self.username,
                      'password': self.password,
                      'locale': 'en_EN',
                      'gfLang': 'en',
                      'platformGameId': '1dfd8e7e-6e1a-4eb1-8c64-03c3b62efd2f',
                      'gameEnvironmentId': '0a31d605-ffaf-43e7-aa02-d06df7116fc8',
                      'autoGameAccountCreation': False}
        response = self.session.post('https://gameforge.com/api/v1/auth/thin/sessions', json=login_data)
        if response.status_code is not 201:
            raise Exception('Bad Login')
        else:
            self.token = response.json()['token']
            self.session.headers.update({'authorization': 'Bearer {}'.format(self.token)})

    def test(self):
        try:
            import test
        except ImportError:
            import ogame.test as test
        test.UnittestOgame.empire = self
        suite = unittest.TestLoader().loadTestsFromModule(test)
        return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    def ogame(self):

        class Ogame:
            version = self.landing_page.find('meta', {'name': 'ogame-version'})
            version = list(re.split(r"\.|-", version['content']))
            for i in range(0, 2):
                version[i] = int(version[i])

            class Speed:
                universe = self.landing_page.find('meta', {'name': 'ogame-universe-speed'})
                universe = int(universe['content'])
                fleet = self.landing_page.find('meta', {'name': 'ogame-universe-speed-fleet'})
                fleet = int(fleet['content'])

            class Donut:
                if 1 == int(self.landing_page.find('meta', {'name': 'ogame-donut-galaxy'})['content']):
                    galaxy = True
                else:
                    galaxy = False
                if 1 == int(self.landing_page.find('meta', {'name': 'ogame-donut-system'})['content']):
                    system = True
                else:
                    system = False

        return Ogame

    def upToDate(self):
        if all(version in self.forOgameVersion for version in self.ogame().version):
            return True
        else:
            return False

    def attacked(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['hostile'] > 0:
            return True
        else:
            return False

    def neutral(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['neutral'] > 0:
            return True
        else:
            return False

    def characterclass(self):
        character = self.landing_page.find_partial(class_='sprite characterclass medium')
        return character['class'][3]

    def planet_ids(self):
        ids = []
        for celestial in self.landing_page.find_all(class_='smallplanet'):
            ids.append(int(celestial['id'].replace('planet-', '')))
        return ids

    def planet_names(self):
        return [planet.text for planet in self.landing_page.find_all(class_='planet-name')]

    def id_by_planet_name(self, name):
        for planet_name, id in zip(OGame.planet_names(self), OGame.planet_ids(self)):
            if planet_name == name:
                return id

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
            names.append(re.search('<b>(.*) \[', name).group(1))
        return names

    def celestial(self, id):
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=overview',
            params={'cp': id}
        ).text
        bs4 = self.BS4(response)
        javascript = bs4.find_all('script', {'type': 'text/javascript'})[14].text
        textContent1 = re.search('textContent\[1] = "(.*)km \(<span>(.*)<(.*)<span>(.*)<', javascript)
        textContent3 = re.search('textContent\[3] = "(.*) \\\\u00b0C bis (.*) \\\\u00b0C";', javascript)

        class Celestial:
            diameter = int(textContent1.group(1).replace('.', ''))
            used = int(textContent1.group(2))
            total = int(textContent1.group(4))
            free = total - used
            temperature = [int(textContent3.group(1)), int(textContent3.group(2))]
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
            if str(id) in moon['href']:
                coordinates = re.search(r'\[(.*)]', moon['title']).group(1)
                coordinates = [int(coords) for coords in coordinates.split(':')]
                coordinates.append(const.destination.moon)
                return coordinates

    def resources(self, id):
        response = self.session.get(self.index_php + 'page=resourceSettings&cp={}'.format(id)).text
        bs4 = self.BS4(response)

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
            darkmatter = to_int(bs4.find(id='resources_darkmatter')['data-raw'])
            energy = to_int(bs4.find(id='resources_energy')['data-raw'])

        return Resources

    def collect_status(self):
        if self == 'on':
            is_possible = True
        else:
            is_possible = False
        if self == 'active':
            in_construction = True
        else:
            in_construction = False
        return is_possible, in_construction

    def supply(self, id):
        response = self.session.get(self.index_php + 'page=ingame&component=supplies&cp={}'.format(id)).text
        bs4 = self.BS4(response)
        levels = [int(level['data-value']) for level in bs4.find_all(class_='level')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Supply:
            def __init__(self, i):
                self.level = levels[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

        class Supplies(object):
            metal_mine = Supply(0)
            crystal_mine = Supply(1)
            deuterium_mine = Supply(2)
            solar_plant = Supply(3)
            fusion_plant = Supply(4)
            metal_storage = Supply(5)
            crystal_storage = Supply(6)
            deuterium_storage = Supply(7)

        return Supplies

    def facilities(self, id):
        response = self.session.get(self.index_php + 'page=ingame&component=facilities&cp={}'.format(id)).text
        bs4 = self.BS4(response)
        levels = [int(level['data-value']) for level in bs4.find_all(class_='level')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Facility:
            def __init__(self, i):
                self.level = levels[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

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
        response = self.session.get('{}page=ingame&component=facilities&cp={}'.format(self.index_php, id)).text
        bs4 = self.BS4(response)
        levels = [int(level['data-value']) for level in bs4.find_all(class_='level')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Facility:
            def __init__(self, i):
                self.level = levels[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

        class Facilities(object):
            robotics_factory = Facility(0)
            shipyard = Facility(1)
            moon_base = Facility(2)
            sensor_phalanx = Facility(3)
            jump_gate = Facility(4)

        return Facilities

    def marketplace(self):
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace'},
        ).text
        token = re.search('var token = "(.*)"', response).group(1)
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace',
                    'tab': 'buying',
                    'action': 'fetchBuyingItems',
                    'token': token,
                    'ajax': 1},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        print(response['content']['marketplace/marketplace_items_buying'])
        bs4 = self.BS4(response['content']['marketplace/marketplace_items_buying'])

        def convert(sprites, quantity):
            bids = []
            for sprite, amount in zip(sprites, quantity):
                amount = amount.replace('.', '')
                if 'metal' in sprite:
                    bids.append(const.resources(metal=amount))
                elif 'crystal' in sprite:
                    bids.append(const.resources(crystal=amount))
                elif 'deuterium' in sprite:
                    bids.append(const.resources(deuterium=amount))
                elif 'ship' in sprite:
                    shipId = int(sprite.replace('ship', ''))
                    bids.append([shipId, amount, 'shipyard'])
                else:
                    continue
            return bids

        ids = [int(id['data-itemid']) for id in bs4.find_all('a', {'data-itemid': True})]
        sums = len(ids)
        quantity = [quant.text for quant in bs4.find_all(class_='text quantity')]
        sprites = [sprite['class'][3] for sprite in bs4.find_all(class_='sprite')]
        offers = convert(sprites=[sprites[i] for i in range(0, sums * 3, 3)],
                         quantity=[quantity[i] for i in range(0, sums * 3, 3)])
        prices = convert(sprites=[sprites[i] for i in range(1, sums * 3, 3)],
                         quantity=[quantity[i] for i in range(1, sums * 3, 3)])
        possibles = []
        for button in bs4.find_all_partial(class_='sprite buttons'):
            if 'disabled' in button['class']:
                possibles.append(False)
            else:
                possibles.append(True)
        bids = []
        for i in range(sums):

            class Bids:
                id = ids[i]
                offer = offers[i]
                price = prices[i]
                is_possible = possibles[i]
                if const.ships.is_ship(offer):
                    is_ships = True
                    is_resources = False
                else:
                    is_ships = False
                    is_resources = True
                list = [id, offer, price, is_possible]

            bids.append(Bids)
        return bids

    def buy_marketplace(self, market_id, id):
        self.session.get(
            url=self.index_php + 'page=ingame&component=marketplace&tab=buying&action=fetchBuyingItems&ajax=1&'
                                 'pagination%5Bpage%5D={}&cp={}'.format(1, id),
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        form_data = {'marketItemId': market_id}
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=marketplace&tab=buying&action=acceptRequest&asJson=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['status'] == 'success':
            return True
        else:
            return False

    def submit_marketplace(self, offer, price, range, id):
        if const.ships.is_ship(offer):
            itemType = 1
            ItemId = const.ships.ship_id(offer)
            quantity = const.ships.ship_amount(offer)
        else:
            itemType = 2
            ItemId = offer.index(max(offer)) + 1  # ItemId 1 = Metall ...
            quantity = max(offer)
        priceType = price.index(max(price)) + 1
        price_form = max(price)
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace',
                    'tab': 'overview',
                    'cp': id}
        ).text
        token = re.search('var token = "(.*)"', response).group(1)
        response = self.session.post(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace',
                    'tab': 'create_offer',
                    'action': 'submitOffer',
                    'asJson': 1},
            data={'marketItemType': 4,
                  'itemType': itemType,
                  'itemId': ItemId,
                  'quantity': quantity,
                  'priceType': priceType,
                  'price': price_form,
                  'token': token,
                  'priceRange': range},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['status'] == 'success':
            return True
        else:
            return False

    def collect_marketplace(self):

        def collectItems(self, tab, action):
            response = self.session.get(
                url=self.index_php,
                params={'page': 'ingame',
                        'component': 'marketplace',
                        'tab': tab}
            ).text
            token = re.search('var token = "(.*)"', response).group(1)
            response = self.session.get(
                url=self.index_php,
                params={'page': 'ingame',
                        'component': 'marketplace',
                        'tab': tab,
                        'action': action,
                        'ajax': 1,
                        'token': token},
                headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
            bs4 = self.BS4(response['content']['marketplace/marketplace_items_history'])
            transactionIds = bs4.find_all('div', {'data-transactionid': True})
            transactionIds = set([int(id['data-transactionid']) for id in transactionIds])
            token = set(bs4.find('div', {'data-token': True}))
            result = []
            for id in transactionIds:
                response = self.session.post(
                    url=self.index_php,
                    params={'page': 'componentOnly',
                            'component': 'marketplace',
                            'action': 'collectItem',
                            'token': token,
                            'asJson': 1},
                    data={'marketTransactionId': id,
                          'token': token},
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                ).json()
                token = response['newToken']
                result.append(response['status'])
            return result

        result = []
        result.extend([collectItems(self, tab='history_buying', action='fetchHistoryBuyingItems')])
        result.extend(collectItems(self, tab='history_selling', action='fetchHistorySellingItems'))
        if 'success' in result:
            return True
        else:
            return False

    def traider(self, id):
        raise Exception("function not implemented yet PLS contribute")

    def research(self):
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame', 'component': 'research', 'cp': OGame.planet_ids(self)[0]}
        ).text
        bs4 = self.BS4(response)
        levels = [int(level['data-value']) for level in bs4.find_all(class_='level')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Research:
            def __init__(self, i):
                self.level = levels[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

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
        response = self.session.get(self.index_php + 'page=ingame&component=shipyard&cp={}'.format(id)).text
        bs4 = self.BS4(response)
        ships_amount = [int(level['data-value']) for level in bs4.find_all(class_='amount')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Ship:
            def __init__(self, i):
                self.amount = ships_amount[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

        class Crawler:
            if id not in OGame.moon_ids(self):
                amount = ships_amount[16]
                data = OGame.collect_status(status[16])
                is_possible = data[0]
                in_construction = data[1]
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
        response = self.session.get(self.index_php + 'page=ingame&component=defenses&cp={}'.format(id)).text
        bs4 = self.BS4(response)
        defences_amount = [int(level['data-value']) for level in bs4.find_all(class_='amount')]
        status = [status['data-status'] for status in bs4.find_all('li', {'class': 'technology'})]

        class Defence:
            def __init__(self, i):
                self.amount = defences_amount[i]
                self.data = OGame.collect_status(status[i])
                self.is_possible = self.data[0]
                self.in_construction = self.data[1]

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

    def galaxy(self, coordinates):
        form_data = {'galaxy': coordinates[0], 'system': coordinates[1]}
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=galaxyContent&ajax=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        html = OGame.HTML(response['galaxy'])
        moons = [int(moon.replace('moon', '')) for moon in html.find_all('rel', 'moon', 'attribute')]

        def collect_player():
            player_names = []
            player_ids = []
            player_ids_count = 0
            allys = html.find_all('rel', 'alliance', 'value')
            moderatorTags = ['A', 's', 'n', 'o', 'u', 'g', 'i', 'I', 'ep', '', 'd', 'v', 'ph', 'f', 'b', 'hp', 'sek.']
            for name in html.find_all('class', 'status_abbr_', 'value'):
                if name not in moderatorTags and 2 < len(name) and name not in allys:
                    name = name.replace('...', '')
                    player_names.append(name)
                    if name not in self.player:
                        player_ids.append(int(html.find_all('id', 'player', 'attribute')
                                              [player_ids_count].replace('player', '')))
                        player_ids_count += 1
                    else:
                        player_ids.append(self.player_id)
            return player_names, player_ids

        def collect_status():
            stati = []
            for status in html.find_all('class', 'row', 'attribute')[5:]:
                if 'rowempty' in status:
                    continue
                elif 'row' == status:
                    stati.append([const.status.active])
                else:
                    activitys = []
                    for activity in [const.status.active, const.status.inactive, const.status.vacation,
                                     const.status.noob, const.status.honorableTarget]:
                        if activity in status and activity != 'active':
                            activitys.append(activity)
                    stati.append(activitys)
            return stati

        def collect_online():
            online_status = []
            for i, planet in enumerate(response['galaxy'].split('rel="planet')[1:]):
                if 'activity minute15' in planet:
                    online_status.append(const.status.online)
                elif 'activity' in planet:
                    online_status.append(const.status.recently)
                else:
                    online_status.append(const.status.offline)
            return online_status

        planets = []
        for planet_pos, planet_name, planet_player, planet_player_id, player_status, planet_status in zip(
                [int(pos.replace('planet', '')) for pos in html.find_all('rel', 'planet', 'attribute')],
                html.find_all('class', 'planetname', 'value'),
                collect_player()[0],
                collect_player()[1],
                collect_online(),
                collect_status()):

            class planet_class:
                position = const.coordinates(coordinates[0], coordinates[1], planet_pos)
                name = planet_name
                player = planet_player
                player_id = planet_player_id
                status = planet_status
                status.append(player_status)
                if planet_pos in moons:
                    moon = True
                else:
                    moon = False
                list = [name, position, player, player_id, status, moon]

            planets.append(planet_class)
        return planets

    def ally(self):
        return self.landing_page.find_all('name', 'ogame-alliance-name', 'attribute', 'content')

    def officers(self):
        raise Exception("function not implemented yet PLS contribute")

    def shop(self):
        raise Exception("function not implemented yet PLS contribute")

    def friendly_fleet(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['friendly'] == 0:
            return []
        response = self.session.get(self.index_php + 'page=ingame&component=movement').text
        html = OGame.HTML(response)
        missions = len(html.find_all('id', 'fleet', 'attribute'))
        fleets = []
        for fleet_id, fleet_mission, fleet_returns, fleet_arrival, fleet_origin, fleet_destination in zip(
                [int(fleet_id.replace('fleet', '')) for fleet_id in html.find_all('id', 'fleet', 'attribute')],
                html.find_all('data-mission-type', '', 'attribute')[-missions:],
                html.find_all('data-return-flight', '', 'attribute')[-missions:],
                html.find_all('class', 'timertooltip', 'attribute', 'title'),
                [html.find_all('href', '&componentgalaxy&galaxy', 'value')[i] for i in range(0, missions * 2, 2)],
                [html.find_all('href', '&componentgalaxy&galaxy', 'value')[i] for i in range(1, missions * 2, 2)]):

            class fleets_class:
                id = fleet_id
                mission = int(fleet_mission)
                diplomacy = const.diplomacy.friendly
                player = self.player_id
                if fleet_returns == '1':
                    returns = True
                else:
                    returns = False
                arrival = datetime.strptime(fleet_arrival, '%d.%m.%Y%H:%M:%S')
                origin = const.convert_to_coordinates(fleet_origin)
                destination = const.convert_to_coordinates(fleet_destination)
                list = [id, mission, diplomacy, player, returns, arrival, origin, destination]

            fleets.append(fleets_class)
        return fleets

    def hostile_fleet(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList'
        ).text
        html = OGame.HTML(response)
        missions = len(html.find_all('id', 'eventRow-', 'attribute'))
        coordinates = [self.celestial_coordinates(id) for id in self.planet_ids() + self.moon_ids()]
        coordinates = [coords[:-1] for coords in coordinates]
        fleets = []
        for player_id, fleet_mission, event_id, fleet_arrival, fleet_origin, fleet_destination in zip(
                html.find_all('class', 'sendMail', 'attribute', 'data-playerId'),
                html.find_all('data-mission-type', '', 'attribute')[-missions:],
                [int(fleet_id.replace('eventRow-', '')) for fleet_id in html.find_all('id', 'eventRow-', 'attribute')],
                html.find_all('data-arrival-time', '', 'attribute'),
                [html.find_all('target', '_top', 'value')[i] for i in range(0, missions * 2, 2)],
                [html.find_all('target', '_top', 'value')[i] for i in range(1, missions * 2, 2)]):

            if const.convert_to_coordinates(fleet_destination) in coordinates:
                class fleets_class:
                    id = event_id
                    mission = int(fleet_mission)
                    diplomacy = const.diplomacy.hostile
                    player = int(player_id)
                    returns = False
                    arrival = datetime.fromtimestamp(int(fleet_arrival))
                    origin = const.convert_to_coordinates(fleet_origin)
                    destination = const.convert_to_coordinates(fleet_destination)
                    list = [id, mission, diplomacy, player, returns, arrival, origin, destination]

                fleets.append(fleets_class)
        return fleets

    def fleet(self):
        fleets = []
        fleets.extend(self.hostile_fleet())
        fleets.extend(self.friendly_fleet())
        return fleets

    def phalanx(self, coordinates, id):
        UserWarning("")
        response = self.session.get(
            url=self.index_php + 'page=phalanx&galaxy={}&system={}&position={}&ajax=1&cp={}'
                .format(coordinates[0], coordinates[1], coordinates[2], id)
        ).text
        html = OGame.HTML(response)
        missions = len(html.find_all('id', 'eventRow-', 'attribute'))
        fleets = []
        for fleet_id, fleet_mission, fleet_returns, fleet_arrival, fleet_origin, fleet_destination in zip(
                html.find_all('id', 'eventRow-', 'attribute'),
                html.find_all('data-mission-type', '', 'attribute'),
                html.find_all('data-return-flight', '', 'attribute'),
                html.find_all('data-arrival-time', '', 'attribute'),
                [html.find_all('class', 'dark_highlight_tablet', 'value')[i] for i in range(0, missions * 3, 3)],
                [html.find_all('class', 'dark_highlight_tablet', 'value')[i] for i in range(2, missions * 3, 3)]):

            class fleets_class:
                id = int(fleet_id.replace('eventRow-', ''))
                mission = int(fleet_mission)
                if fleet_returns == 'true':
                    returns = True
                else:
                    returns = False
                arrival = datetime.fromtimestamp(int(fleet_arrival))
                origin = const.convert_to_coordinates(fleet_origin)
                destination = const.convert_to_coordinates(fleet_destination)
                list = [id, mission, returns, arrival, origin, destination]

            fleets.append(fleets_class)
        return fleets

    def messages(self, message_type, page):
        form_data = {'messageId': -1,
                     'tabid': message_type,
                     'action': 107,
                     'pagination': page,
                     'ajax': 1}
        response = self.session.post(
            url=self.index_php + 'page=messages',
            data=form_data
        ).text
        html = OGame.HTML(response)
        return html

    def send_message(self, player_id, msg):
        response = self.session.get(self.index_php + 'page=chat').text
        html = OGame.HTML(response)
        chat_token = None
        for line in html.find_all('type', 'textjavascript', 'value'):
            if 'ajaxChatToken' in line:
                chat_token = line.split('ajaxChatToken=')[1].split('"')[1]
                break
        form_data = {'playerId': player_id,
                     'text': msg,
                     'mode': 1,
                     'ajax': 1,
                     'token': chat_token}
        response = self.session.post(
            url=self.index_php + 'page=ajaxChat',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 'OK' in response['status']:
            return True
        else:
            return False

    def spyreports(self):
        html = OGame.messages(self, const.messages.spy_reports, 1)
        spyreports = []
        for message in html.find_all('data-msg-id', '', 'attribute'):
            response = self.session.get(
                url=self.index_php + 'page=messages&messageId={}&tabid={}&ajax=1'
                    .format(message, const.messages.spy_reports)
            ).text
            spy_html = OGame.HTML(response)
            fright = spy_html.find_all('class', 'fright', 'value')
            fright.pop()
            if len(fright) > 10:  # non Spyreports are less than 10

                class spy_report_class:
                    id = message
                    coordinates = const.convert_to_coordinates(response)
                    if spy_html.find_all('class', 'planetIcon', 'attribute') is not []:
                        coordinates.append(const.destination.planet)
                    else:
                        coordinates.append(const.destination.moon)
                    time = datetime.strptime(fright[5], '%d.%m.%Y%H:%M:%S')
                    resources = spy_html.find_all('class', 'resource_list', 'attribute', 'title')
                    resources = [resources[0], resources[1], resources[2]]
                    resources = [int(resource.replace('.', '')) for resource in resources]
                    tech = []
                    fleets = spy_html.find_all('class', 'tech', 'attribute')
                    for fleet in fleets:
                        tech.append(const.convert_tech(int(fleet.replace('tech', '')), 'shipyard'))
                    defences = spy_html.find_all('class', 'fright', 'value')
                    for defence in defences:
                        if not defence.isdigit():
                            defence = defences.remove(defence)
                    buildings = spy_html.find_all('class', 'building', 'attribute')
                    for building in buildings:
                        if building != 'building_imagefloat_left':
                            tech.append(const.convert_tech(int(building.replace('building', '')), 'supplies'))
                    researchings = spy_html.find_all('class', 'research', 'attribute')
                    for research in researchings:
                        if research != 'research_imagefloat_left':
                            tech.append(const.convert_tech(int(research.replace('research', '')), 'research'))
                    technology = dict((tech, amount) for tech, amount in zip(tech, fright[7:]))
                    list = [id, time, coordinates, resources, technology]

                spyreports.append(spy_report_class)
        return spyreports

    def send_fleet(self, mission, id, where, ships, resources=[0, 0, 0], speed=10, holdingtime=0):
        response = self.session.get(self.index_php + 'page=ingame&component=fleetdispatch&cp={}'.format(id)).text
        html = OGame.HTML(response)
        sendfleet_token = None
        for line in html.find_all('type', 'textjavascript', 'value'):
            if 'fleetSendingToken' in line:
                sendfleet_token = line.split('fleetSendingToken=')[1].split('"')[1]
                break
        form_data = {'token': sendfleet_token}
        for ship in ships:
            ship_type = 'am{}'.format(ship[0])
            form_data.update({ship_type: ship[1]})
        form_data.update({'galaxy': where[0],
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
                          'holdingtime': holdingtime})
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=fleetdispatch&action=sendFleet&ajax=1&asJson=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        return response['success']

    def return_fleet(self, fleet_id):
        self.session.get(self.index_php + 'page=ingame&component=movement&return={}'.format(fleet_id))

    def build(self, what, id):
        type = what[0]
        amount = what[1]
        component = what[2]
        response = self.session.get(self.index_php + 'page=ingame&component={}&cp={}'.format(component, id)).text
        html = OGame.HTML(response)
        build_token = None
        for line in html.find_all('type', 'javascript', 'value'):
            if 'urlQueueAdd' in line:
                build_token = line.split('token=')[1].split('\'')[0]
                break
        build_url = self.index_php + 'page=ingame&component={}&modus=1&token={}&type={}&menge={}' \
            .format(component, build_token, type, amount)
        self.session.get(build_url)

    def collect_rubble_field(self, id):
        self.session.get(
            url=self.index_php + 'page=ajax&component=repairlayer&component=repairlayer&ajax=1'
                                 '&action=startRepairs&asJson=1&cp={}'.format(id),
            headers={'X-Requested-With': 'XMLHttpRequest'})

    def is_logged_in(self):
        response = self.session.get('https://lobby.ogame.gameforge.com/api/users/me/accounts').json()
        if 'error' in response:
            return False
        else:
            return True

    def relogin(self, universe=None):
        if universe is None:
            universe = self.universe
        OGame.__init__(self, universe, self.username, self.password, self.user_agent, self.proxy)
        return OGame.is_logged_in(self)

    def logout(self):
        self.session.get(self.index_php + 'page=logout')
        self.session.put('https://lobby.ogame.gameforge.com/api/users/me/logout')
        self.token = None
        self.session = requests.Session()
        return not OGame.is_logged_in(self)
