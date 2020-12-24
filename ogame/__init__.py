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

    def test(self):
        try:
            import pruebas
        except ImportError:
            import ogame.test as test
        test.UnittestOgame.empire = self
        suite = unittest.TestLoader().loadTestsFromModule(test)
        return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    def server(self):

        class Server:
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

        return Server

    def attacked(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['hostile']:
            return True
        else:
            return False

    def neutral(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['neutral']:
            return True
        else:
            return False

    def friendly(self):
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList&action=fetchEventBox&ajax=1&asJson=1',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if 0 < response['friendly']:
            return True
        else:
            return False

    def characterclass(self):
        character = self.landing_page.find_partial(class_='sprite characterclass medium')
        return character['class'][3]

    def rank(self):
        rank = self.landing_page.find(id='bar')
        rank = rank.find_all('li')[1].text
        rank = re.search('\((.*)\)', rank).group(1)
        return int(rank)

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
        textContent1 = re.search(r'textContent\[1] = "(.*)km \(<span>(.*)<(.*)<span>(.*)<', javascript)
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
            if moon and str(id) in moon['href']:
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
        levels = [int(level['data-value']) for level in bs4.find_all('span', {'data-value': True})]
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

    def marketplace_listings(self, id):
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace',
                    'cp': id},
        ).text
        token = re.search('var token = "(.*)"', response).group(1)
        response = self.session.get(
            url=self.index_php,
            params={'page': 'ingame',
                    'component': 'marketplace',
                    'tab': 'buying',
                    'action': 'fetchBuyingItems',
                    'token': token,
                    'ajax': 1,
                    'cp': id},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        bs4 = self.BS4(response['content']['marketplace/marketplace_items_buying'])
        return bs4

    def marketplace(self, id):
        bs4 = self.marketplace_listings(id)

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

        # every 3 + n [n={0,1}] is the offer n=0 or the price n=1
        def keep_every_3_item(list, offset):
            every_3_item = [list[i] for i in range(offset, sums * 3, 3)]
            return every_3_item

        offers = convert(sprites=keep_every_3_item(sprites, 0),
                         quantity=keep_every_3_item(quantity, 0))
        prices = convert(sprites=keep_every_3_item(sprites, 1),
                         quantity=keep_every_3_item(quantity, 1))

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

    def buy_marketplace(self, marketid, id):
        bs4 = self.marketplace_listings(id)
        token = bs4.find('a', {'data-itemid': marketid})['data-token']
        response = self.session.post(
            url=self.index_php + f'page=ingame&component=marketplace&tab=buying&action=acceptRequest&asJson=1',
            data={'marketItemId': marketid,
                  'token': token},
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
            params={
                'page': 'ingame',
                'component': 'marketplace',
                'tab': 'create_offer',
                'action': 'submitOffer',
                'asJson': 1},
            data={
                'marketItemType': 4,
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
            transactionIds = set([id['data-transactionid'] for id in transactionIds])
            token = re.search('collectItem&token=(.*)"', bs4.text).group(1)
            result = []
            for id in transactionIds:
                response = self.session.post(
                    url=self.index_php,
                    params={'page': 'componentOnly',
                            'component': 'marketplace',
                            'action': 'collectItem',
                            'token': token,
                            'asJson': 1},
                    data={'marketTransactionId': int(id),
                          'token': token},
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                ).json()
                token = response['newToken']
                result.append(response['status'])
            return result

        result = []
        result.extend(collectItems(self, tab='history_buying', action='fetchHistoryBuyingItems'))
        result.extend(collectItems(self, tab='history_selling', action='fetchHistorySellingItems'))
        if 'success' in result:
            return True
        else:
            return False

    def traider(self, id):
        raise NotImplementedError("function not implemented yet PLS contribute")

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

    def galaxy(self, coords):
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=galaxyContent&ajax=1',
            data={'galaxy': coords[0], 'system': coords[1]},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        bs4 = self.BS4(response['galaxy'])

        positions = bs4.find_all_partial(rel='planet')
        positions = [pos['rel'] for pos in positions]
        positions = [re.search('planet(.*)', pos).group(1) for pos in positions]
        positions = [const.coordinates(coords[0], coords[1], int(pos), const.destination.planet) for pos in positions]

        planet_names = bs4.find_all_partial(rel='planet')
        planet_names = [name.h1.span.text for name in planet_names]

        players = bs4.find_all_partial(id='player')
        player_names = [name.h1.span.text for name in players]
        player_ids = [id['id'] for id in players]
        player_ids = [int(re.search('player(.*)', id).group(1)) for id in player_ids]

        player_rank = bs4.select(".rank a")
        player_rank = {int(re.search('searchRelId=(.*)', a['href']).group(1)): int(a.text) for a in player_rank}

        planet_status = []
        for status in bs4.find_all(class_='row'):
            status = status['class']
            status.remove('row')
            if 'empty_filter' in status:
                continue
            elif len(status) is 0:
                planet_status.append([const.status.yourself])
            else:
                status = [re.search('(.*)_filter', sta).group(1) for sta in status]
                planet_status.append(status)

        moon_pos = bs4.find_all_partial(rel='moon')
        moon_pos = [pos['rel'] for pos in moon_pos]
        moon_pos = [int(re.search('moon(.*)', pos).group(1)) for pos in moon_pos]

        planets = []
        for i in range(len(player_ids)):

            class Position:
                position = positions[i]
                name = planet_names[i]
                player = player_names[i]
                player_id = player_ids[i]
                rank = player_rank.get(player_id, None)
                status = planet_status[i]
                if position[2] in moon_pos:
                    moon = True
                else:
                    moon = False
                list = [name, position, player, player_id, rank, status, moon]

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

    def fleet_coordinates(self, event, coordsclass):
        coordinate = [coords.find(class_=coordsclass).a.text for coords in event]
        coordinate = [const.convert_to_coordinates(coords) for coords in coordinate]
        destination = [dest.find('figure', {'class': 'planetIcon'}) for dest in event]
        destination = [const.convert_to_destinations(dest['class']) for dest in destination]
        coordinates = []
        for coords, dest in zip(coordinate, destination):
            coords.append(dest)
            coordinates.append(coords)

        return coordinates

    def friendly_fleet(self):
        if not self.friendly():
            return []
        response = self.session.get(self.index_php + 'page=ingame&component=movement').text
        bs4 = self.BS4(response)
        fleetDetails = bs4.find_all(class_='fleetDetails')
        fleet_ids = bs4.find_all_partial(id="fleet")
        fleet_ids = [id['id'] for id in fleet_ids]
        fleet_ids = [int(re.search('fleet(.*)', id).group(1)) for id in fleet_ids]

        mission_types = [int(event['data-mission-type']) for event in fleetDetails]
        return_flights = [bool(event['data-return-flight']) for event in fleetDetails]

        arrival_times = [int(event['data-arrival-time']) for event in fleetDetails]
        arrival_times = [datetime.fromtimestamp(timestamp) for timestamp in arrival_times]

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
                list = [id, mission, diplomacy, player_name, player_id, returns, arrival, origin, destination]

            fleets.append(Fleets)
        return fleets

    def hostile_fleet(self):
        if not self.attacked():
            return []
        response = self.session.get(
            url=self.index_php + 'page=componentOnly&component=eventList'
        ).text
        bs4 = self.BS4(response)

        eventFleet = bs4.find_all('span', class_='hostile')
        eventFleet = [child.parent.parent for child in eventFleet]

        fleet_ids = [id['id'] for id in eventFleet]
        fleet_ids = [int(re.search('eventRow-(.*)', id).group(1)) for id in fleet_ids]

        arrival_times = [int(event['data-arrival-time']) for event in eventFleet]
        arrival_times = [datetime.fromtimestamp(timestamp) for timestamp in arrival_times]

        destinations = self.fleet_coordinates(eventFleet, 'destCoords')
        origins = self.fleet_coordinates(eventFleet, 'coordsOrigin')

        player_ids = [int(id.find(class_='sendMail').a['data-playerid']) for id in eventFleet]
        player_names = [name.find(class_='sendMail').a['title'] for name in eventFleet]

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
                list = [id, mission, diplomacy, player_name, player_id, returns, arrival, origin, destination]

            fleets.append(Fleets)
        return fleets

    def fleet(self):
        fleets = []
        fleets.extend(self.hostile_fleet())
        fleets.extend(self.friendly_fleet())
        return fleets

    def phalanx(self, coordinates, id):
        raise NotImplemented('Phalanx get you banned ig used with invalid parameters')

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

    def spyreports(self):
        response = self.session.get(
            url=self.index_php,
            params={'page': 'messages',
                    'tab': 20,
                    'ajax': 1}
        ).text
        bs4 = self.BS4(response)
        report_links = [link['href'] for link in bs4.find_all_partial(href='page=messages&messageId')]

        reports = []
        for link in report_links:
            response = self.session.get(link).text
            bs4 = self.BS4(response)
            technologys = [tech['class'][0] for tech in bs4.find_all('img')]
            amounts = [tech.parent.parent.find_all('span')[1].text for tech in bs4.find_all('img')]

            class Report:
                fright = [(tech, amount) for tech, amount in zip(technologys, amounts)]

            reports.append(Report)

        return reports

    def send_fleet(self, mission, id, where, ships, resources=(0, 0, 0), speed=10, holdingtime=0):
        response = self.session.get(self.index_php + 'page=ingame&component=fleetdispatch&cp={}'.format(id)).text
        sendfleet_token = re.search('var fleetSendingToken = "(.*)"', response).group(1)
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
        build_token = re.search("var urlQueueAdd = (.*)token=(.*)'", response).group(2)
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
