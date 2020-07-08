import re
import requests
from datetime import datetime

try:
    import constants as const
except ImportError:
    import ogame.constants as const


class OGame(object):
    def __init__(self, universe, username, password, user_agent=None, proxy='', language=None):
        self.universe = universe
        self.username = username
        self.password = password
        self.user_agent = user_agent
        self.proxy = proxy
        self.language = language
        self.session = requests.Session()
        self.session.proxies.update({'https': self.proxy})
        self.chat_token = None
        if self.user_agent is None:
            self.user_agent = {
                'User-Agent':
                    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/83.0.4103.97 Mobile Safari/537.36'}
        self.session.headers.update(self.user_agent)

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
        self.session.headers.update({'authorization': 'Bearer {}'.format(response.json()['token'])})

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
            for account in accounts:
                if account['server']['number'] == self.server_number and account['server']['language'] == self.language:
                    self.server_id = account['id']
                    break
                elif account['server']['number'] == self.server_number and self.language is None:
                    self.server_id = account['id']
                    self.language = account['server']['language']
                    break
        except AttributeError:
            raise Exception("Universe not found")

        login_link = self.session.get(
            'https://lobby.ogame.gameforge.com/api/users/me/loginLink?'
            'id={}'
            '&server[language]={}'
            '&server[number]={}'
            '&clickedButton=account_list'
            .format(self.server_id, self.language, self.server_number)
        ).json()
        self.landing_page = self.session.get(login_link['url']).text
        self.index_php = 'https://s{}-{}.ogame.gameforge.com/game/index.php?' \
            .format(self.server_number, self.language)
        self.landing_page = OGame.HTML(self.session.get(self.index_php + 'page=ingame').text)
        self.player = self.landing_page.find_all('class', 'overlaytextBeefy', 'value')
        self.player_id = self.landing_page.find_all('name', 'ogame-player-id', 'attribute', 'content')

    class HTML:
        def __init__(self, response):
            self.parsed = {}
            for index, html in enumerate(response.split('<')):
                element = html.replace('/', '').replace('\n', '')
                tag = element.split('>')[0]
                attribute = tag.split(' ')
                if ' ' in tag:
                    tag = tag.split(' ')[0]
                del attribute[0]
                attribute = ' '.join(attribute).replace('=', '').replace(' ', '').split('"')
                attributes = {}
                for i in range(0, len(attribute), 2):
                    try:
                        attributes.update({attribute[i]: attribute[i + 1]})
                    except IndexError:
                        break
                if len(element.split('>')) > 1:
                    value = element.split('>')[1]
                else:
                    value = None
                self.parsed.update({index: {'tag': tag, 'attribute': attributes, 'value': value}})

        def find_all(self, attribute_tag, value, result, same_element_attribute=None, exact=False):
            attributes = []

            def append_attributes():
                if result == 'attribute' and same_element_attribute is None:
                    attributes.append(line[result][attribute_tag])
                elif result == 'attribute':
                    attributes.append(line[result][same_element_attribute])
                else:
                    val = line[result].replace(' ', '')
                    if val is not '':
                        attributes.append(val)

            for line in self.parsed.values():
                try:
                    if attribute_tag in line['attribute']:
                        if value in line['attribute'][attribute_tag] and exact is False:
                            append_attributes()
                        elif value == line['attribute'][attribute_tag] and exact is True:
                            append_attributes()
                except KeyError:
                    continue
            return attributes

    def test(self):
        try:
            import ogame.test as test
        except ImportError:
            import test
        empire = OGame(self.universe, self.username, self.password, self.user_agent, self.proxy)
        test.pyogame(empire)

    def version(self):
        from pip._internal import main as pip
        print(pip(['show', 'ogame']))

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

    def speed(self):
        class speed:
            universe = int(self.landing_page.find_all('content', '', 'attribute')[6])
            fleet = int(self.landing_page.find_all('content', '', 'attribute')[7])

        return speed

    def planet_ids(self):
        planets = self.landing_page.find_all('id', 'planet-', 'attribute')
        return [int(planet.replace('planet-', '')) for planet in planets]

    def planet_names(self):
        return self.landing_page.find_all('class', 'planet-name', 'value')

    def id_by_planet_name(self, name):
        for planet_name, id in zip(OGame.planet_names(self), OGame.planet_ids(self)):
            if planet_name == name:
                return id

    def moon_ids(self):
        moons = self.landing_page.find_all('class', 'moonlink', 'attribute', 'href')
        return [moon_id.split('cp')[1] for moon_id in moons]

    def moon_names(self):
        names = []
        for name in self.landing_page.find_all('class', 'moonlink', 'attribute', 'title'):
            names.append(name.split(';')[2].split('[')[0])
        return names

    def celestial_coordinates(self, id):
        celestial = self.landing_page.find_all('title', 'componentgalaxy&amp;cp{}'.format(id), 'attribute')
        coordinates = celestial[0].split('componentgalaxy&amp;cp{}&amp;'.format(id))[1].split('&quot;')[0] \
            .replace('&amp', '').replace('galaxy', '').replace('system', '').replace('position', '').split(';')
        if 'moon' in self.landing_page.find_all('title', 'galaxy&amp;cp{}'.format(id), 'attribute', 'class')[0]:
            coordinates.append(const.destination.moon)
        else:
            coordinates.append(const.destination.planet)
        return coordinates

    def resources(self, id):
        response = self.session.get(self.index_php + 'page=resourceSettings&cp={}'.format(id)).text
        html = OGame.HTML(response)

        def to_int(string):
            return int(float(string.replace('M', '000').replace('n', '')))

        class resources:
            resources = [html.find_all('id', 'resources_metal', 'attribute', 'data-raw')[0],
                         html.find_all('id', 'resources_crystal', 'attribute', 'data-raw')[0],
                         html.find_all('id', 'resources_deuterium', 'attribute', 'data-raw')[0]]
            resources = [to_int(resource) for resource in resources]
            metal = resources[0]
            crystal = resources[1]
            deuterium = resources[2]
            darkmatter = to_int(html.find_all('id', 'resources_darkmatter', 'attribute', 'data-raw')[0])
            energy = to_int(html.find_all('id', 'resources_energy', 'attribute', 'data-raw')[0])

        return resources

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
        html = OGame.HTML(response)
        levels = [int(level) for level in html.find_all('class', 'level', 'attribute', 'data-value', exact=True)]
        status = html.find_all('data-technology', '', 'attribute', 'data-status')

        class metal_mine_class:
            level = levels[0]
            data = OGame.collect_status(status[0])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.metal_mine, level=level)

        class crystal_mine_class:
            level = levels[1]
            data = OGame.collect_status(status[1])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.crystal_mine, level=level)

        class deuterium_mine_class:
            level = levels[2]
            data = OGame.collect_status(status[2])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.deuterium_mine, level=level)

        class solar_plant_class:
            level = levels[3]
            data = OGame.collect_status(status[3])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.solar_plant, level=level)

        class fusion_plant_class:
            level = levels[4]
            data = OGame.collect_status(status[4])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.fusion_plant, level=level)

        class metal_storage_class:
            level = levels[5]
            data = OGame.collect_status(status[7])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.metal_storage, level=level)

        class crystal_storage_class:
            level = levels[6]
            data = OGame.collect_status(status[8])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.crystal_storage, level=level)

        class deuterium_storage_class:
            level = levels[7]
            data = OGame.collect_status(status[9])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.deuterium_storage, level=level)

        class supply_buildings(object):
            metal_mine = metal_mine_class
            crystal_mine = crystal_mine_class
            deuterium_mine = deuterium_mine_class
            solar_plant = solar_plant_class
            fusion_plant = fusion_plant_class
            metal_storage = metal_storage_class
            crystal_storage = crystal_storage_class
            deuterium_storage = deuterium_storage_class

        return supply_buildings

    def facilities(self, id):
        response = self.session.get(self.index_php + 'page=ingame&component=facilities&cp={}'.format(id)).text
        html = OGame.HTML(response)
        levels = [int(level) for level in html.find_all('class', 'level', 'attribute', 'data-value', exact=True)]
        status = html.find_all('data-technology', '', 'attribute', 'data-status')

        class robotics_factory_class:
            level = levels[0]
            data = OGame.collect_status(status[0])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.robotics_factory, level=level)

        class shipyard_class:
            level = levels[1]
            data = OGame.collect_status(status[1])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.shipyard, level=level)

        class research_laboratory_class:
            level = levels[2]
            data = OGame.collect_status(status[2])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.research_laboratory, level=level)

        class alliance_depot_class:
            level = levels[3]
            data = OGame.collect_status(status[3])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.alliance_depot, level=level)

        class missile_silo_class:
            level = levels[4]
            data = OGame.collect_status(status[4])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.missile_silo, level=level)

        class nanite_factory_class:
            level = levels[5]
            data = OGame.collect_status(status[5])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.nanite_factory, level=level)

        class terraformer_class:
            level = levels[6]
            data = OGame.collect_status(status[6])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.terraformer, level=level)

        class repair_dock_class:
            level = levels[7]
            data = OGame.collect_status(status[7])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.repair_dock, level=level)

        class facilities_buildings(object):
            robotics_factory = robotics_factory_class
            shipyard = shipyard_class
            research_laboratory = research_laboratory_class
            alliance_depot = alliance_depot_class
            missile_silo = missile_silo_class
            nanite_factory = nanite_factory_class
            terraformer = terraformer_class
            repair_dock = repair_dock_class

        return facilities_buildings

    def moon_facilities(self, id):
        response = self.session.get('{}page=ingame&component=facilities&cp={}'.format(self.index_php, id)).text
        html = OGame.HTML(response)
        levels = [int(level) for level in html.find_all('class', 'level', 'attribute', 'data-value', exact=True)]
        status = html.find_all('data-technology', '', 'attribute', 'data-status')

        class robotics_factory_class:
            level = levels[0]
            data = OGame.collect_status(status[0])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.robotics_factory, level=level)

        class shipyard_class:
            level = levels[1]
            data = OGame.collect_status(status[1])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.shipyard, level=level)

        class moon_base_class:
            level = levels[2]
            data = OGame.collect_status(status[2])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.moon_base, level=level)

        class sensor_phalanx_class:
            level = levels[3]
            data = OGame.collect_status(status[3])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.sensor_phalanx, level=level)

        class jump_gate_class:
            level = levels[4]
            data = OGame.collect_status(status[4])
            is_possible = data[0]
            in_construction = data[1]
            cost = const.price(const.buildings.jump_gate, level=level)

        class moon_facilities_buildings(object):
            robotics_factory = robotics_factory_class
            shipyard = shipyard_class
            moon_base = moon_base_class
            sensor_phalanx = sensor_phalanx_class
            jump_gate = jump_gate_class

        return moon_facilities_buildings

    def marketplace(self, id, page):
        biddings = []
        response = self.session.get(
            url=self.index_php + 'page=ingame&component=marketplace&tab=buying&action=fetchBuyingItems&ajax=1&'
                                 'pagination%5Bpage%5D={}&cp={}'.format(page, id),
            headers={'X-Requested-With': 'XMLHttpRequest'}).json()
        def item_type(item):
            type = None
            if 'sprite ship small ' in item:
                type = 'ship', int(item[29:32])
            elif 'metal' in item:
                type = 'resources', 'metal'
            elif 'crystal' in item:
                type = 'resources', 'crystal'
            elif 'deuterium' in item:
                type = 'resources', 'deuterium'
            return type

        items = response['content']['marketplace/marketplace_items_buying'].split('<div class="row item og-hline">')
        del items[0]
        for item in items:
            id_int = item.find('<a data-itemid=')
            ships_resources_marker_string = 'class="sprite '
            class_sprite = []
            for re_obj in re.finditer(ships_resources_marker_string, item):
                class_sprite.append(item[re_obj.start(): re_obj.end() + 40])
            to_buy_item_type = item_type(class_sprite[0])
            to_pay_item_type = item_type(class_sprite[1])

            quantity_marker_string = 'text quantity'
            text_quantity = []
            for re_obj in re.finditer(quantity_marker_string, item):
                text_quantity.append(item[re_obj.start(): re_obj.end() + 40])
            to_buy_item_amount = text_quantity[0].split('>')[1].split('<')[0].replace('.', '')
            to_pay_item_amount = text_quantity[1].split('>')[1].split('<')[0].replace('.', '')

            class bid:
                id = item[id_int + 16: id_int + 25].split('"')[0]
                offer = None
                price = None
                is_ships = False
                is_resources = False
                is_possible = False
                if to_buy_item_type[0] == 'ship':
                    is_ships = True
                    offer = to_buy_item_type[1], to_buy_item_amount, 'shipyard'
                else:
                    is_resources = True
                    if 'metal' in to_buy_item_type[1]:
                        offer = const.resources(metal=to_buy_item_amount)
                    elif 'crystal' in to_buy_item_type[1]:
                        offer = const.resources(crystal=to_buy_item_amount)
                    elif 'deuterium' in to_buy_item_type[1]:
                        offer = const.resources(deuterium=to_buy_item_amount)

                if 'metal' in to_pay_item_type[1]:
                    price = const.resources(metal=to_pay_item_amount)
                elif 'crystal' in to_pay_item_type[1]:
                    price = const.resources(crystal=to_pay_item_amount)
                elif 'deuterium' in to_pay_item_type[1]:
                    price = const.resources(deuterium=to_pay_item_amount)

                if 'enabled' in class_sprite[2]:
                    is_possible = True

            biddings.append(bid)
        return biddings

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
        ItemId = None
        quantity = None
        priceType = None
        price_form = None
        self.session.get(self.index_php + 'page=ingame&component=marketplace&tab=overview&cp={}'.format(id))
        if const.ships.is_ship(offer):
            itemType = 1
            ItemId = const.ships.ship_id(offer)
            quantity = const.ships.ship_amount(offer)
        else:
            itemType = 2
            for i, res in enumerate(offer):
                if res != 0:
                    ItemId = i + 1
                    quantity = res
                    break
        for i, res in enumerate(price):
            if res != 0:
                priceType = i + 1
                price_form = res
                break
        form_data = {'marketItemType': 4,
                     'itemType': itemType,
                     'itemId': ItemId,
                     'quantity': quantity,
                     'priceType': priceType,
                     'price': price_form,
                     'priceRange': range}
        response = self.session.post(
            url=self.index_php + 'page=ingame&component=marketplace&tab=create_offer&action=submitOffer&asJson=1',
            data=form_data,
            headers={'X-Requested-With': 'XMLHttpRequest'}
        ).json()
        if response['status'] == 'success':
            return True
        else:
            return False

    def collect_marketplace(self):
        to_collect_market_ids = []
        history_pages = ['history_buying', 'history_selling']
        action = ['fetchHistoryBuyingItems', 'fetchHistorySellingItems']
        collect = ['collectItem', 'collectPrice']
        response = False
        for page, action, collect in zip(history_pages, action, collect):
            response = self.session.get(
                url=self.index_php + 'page=ingame&component=marketplace&tab={}&action={}&ajax=1&pagination%5Bpage%5D=1'
                    .format(page, action, OGame.planet_ids(self)[0]),
                headers={'X-Requested-With': 'XMLHttpRequest'}
            ).json()
            items = response['content']['marketplace/marketplace_items_history'].split('data-transactionid=')
            del items[0]
            for item in items:
                if 'buttons small enabled' in item:
                    to_collect_market_ids.append(int(item[1:10].split('"')[0]))
            for id in to_collect_market_ids:
                form_data = {'marketTransactionId': id}
                response = self.session.post(
                    url=self.index_php + 'page=componentOnly&component=marketplace&action={}&asJson=1'.format(collect),
                    data=form_data,
                    headers={'X-Requested-With': 'XMLHttpRequest'}
                ).json()

        if not to_collect_market_ids:
            return False
        elif response['status'] == 'success':
            return True
        else:
            return False

    def traider(self, id):
        raise Exception("function not implemented yet PLS contribute")

    def research(self):
        response = self.session.get(
            url=self.index_php +
            'page=ingame&component=research&cp={}'.format(
                OGame.planet_ids(self)[0])
        ).text
        html = OGame.HTML(response)
        research_level = [int(level)
                          for level in html.find_all('class', 'level', 'attribute', 'data-value', exact=True)]
        status = html.find_all('data-technology', '',
                               'attribute', 'data-status')

        class research_energy_class:
            level = research_level[0]
            data = OGame.collect_status(status[0])
            is_possible = data[0]
            in_construction = data[1]

        class research_laser_class:
            level = research_level[1]
            data = OGame.collect_status(status[1])
            is_possible = data[0]
            in_construction = data[1]

        class research_ion_class:
            level = research_level[2]
            data = OGame.collect_status(status[2])
            is_possible = data[0]
            in_construction = data[1]

        class research_hyperspace_class:
            level = research_level[3]
            data = OGame.collect_status(status[3])
            is_possible = data[0]
            in_construction = data[1]

        class research_plasma_class:
            level = research_level[4]
            data = OGame.collect_status(status[4])
            is_possible = data[0]
            in_construction = data[1]

        class research_combustion_drive_class:
            level = research_level[5]
            data = OGame.collect_status(status[5])
            is_possible = data[0]
            in_construction = data[1]

        class research_impulse_drive_class:
            level = research_level[6]
            data = OGame.collect_status(status[6])
            is_possible = data[0]
            in_construction = data[1]

        class research_hyperspace_drive_class:
            level = research_level[7]
            data = OGame.collect_status(status[7])
            is_possible = data[0]
            in_construction = data[1]

        class research_espionage_class:
            level = research_level[8]
            data = OGame.collect_status(status[8])
            is_possible = data[0]
            in_construction = data[1]

        class research_computer_class:
            level = research_level[9]
            data = OGame.collect_status(status[9])
            is_possible = data[0]
            in_construction = data[1]

        class research_astrophysics_class:
            level = research_level[10]
            data = OGame.collect_status(status[10])
            is_possible = data[0]
            in_construction = data[1]

        class research_research_network_class:
            level = research_level[11]
            data = OGame.collect_status(status[11])
            is_possible = data[0]
            in_construction = data[1]

        class research_graviton_class:
            level = research_level[12]
            data = OGame.collect_status(status[12])
            is_possible = data[0]
            in_construction = data[1]

        class research_weapons_class:
            level = research_level[13]
            data = OGame.collect_status(status[13])
            is_possible = data[0]
            in_construction = data[1]

        class research_shielding_class:
            level = research_level[14]
            data = OGame.collect_status(status[14])
            is_possible = data[0]
            in_construction = data[1]

        class research_armor_class:
            level = research_level[15]
            data = OGame.collect_status(status[15])
            is_possible = data[0]
            in_construction = data[1]

        class research_class(object):
            energy = research_energy_class
            laser = research_laser_class
            ion = research_ion_class
            hyperspace = research_hyperspace_class
            plasma = research_plasma_class
            combustion_drive = research_combustion_drive_class
            impulse_drive = research_impulse_drive_class
            hyperspace_drive = research_hyperspace_drive_class
            espionage = research_espionage_class
            computer = research_computer_class
            astrophysics = research_astrophysics_class
            research_network = research_research_network_class
            graviton = research_graviton_class
            weapons = research_weapons_class
            shielding = research_shielding_class
            armor = research_armor_class

        return research_class

    def ships(self, id):
        response = self.session.get(self.index_php + 'page=ingame&component=shipyard&cp={}'.format(id)).text
        html = OGame.HTML(response)
        ships_amount = html.find_all('class', 'amount', 'attribute', 'data-value', exact=True)
        ships_amount = [int(ship) for ship in ships_amount]

        class ships_class(object):
            light_fighter = ships_amount[0]
            heavy_fighter = ships_amount[1]
            cruiser = ships_amount[2]
            battleship = ships_amount[3]
            interceptor = ships_amount[4]
            bomber = ships_amount[5]
            destroyer = ships_amount[6]
            deathstar = ships_amount[7]
            reaper = ships_amount[8]
            explorer = ships_amount[9]
            small_transporter = ships_amount[10]
            large_transporter = ships_amount[11]
            colonyShip = ships_amount[12]
            recycler = ships_amount[13]
            espionage_probe = ships_amount[14]
            solarSatellite = ships_amount[15]
            if id not in OGame.moon_ids(self):
                crawler = ships_amount[16]
            else:
                crawler = 0

        return ships_class

    def defences(self, id):
        response = self.session.get(self.index_php + 'page=ingame&component=defenses&cp={}'.format(id)).text
        html = OGame.HTML(response)
        defences_amount = html.find_all('class', 'amount', 'attribute', 'data-value', exact=True)
        defences_amount = [int(ship) for ship in defences_amount]

        class defences_class(object):
            rocket_launcher = defences_amount[0]
            laser_cannon_light = defences_amount[1]
            laser_cannon_heavy = defences_amount[2]
            gauss_cannon = defences_amount[3]
            ion_cannon = defences_amount[4]
            plasma_cannon = defences_amount[5]
            shield_dome_small = defences_amount[6]
            shield_dome_large = defences_amount[7]
            missile_interceptor = defences_amount[8]
            missile_interplanetary = defences_amount[9]

        return defences_class

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
            for name in html.find_all('class', 'status_abbr_', 'value'):
                if name not in ['A', 's', 'n', 'o', 'u', 'g', 'i', 'I', 'ep', ''] and name not in allys:
                    player_names.append(name)
                    if self.player != name:
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

        planets = []
        for planet_pos, planet_name, planet_player, planet_player_id, planet_status in zip(
                [int(pos.replace('planet', '')) for pos in html.find_all('rel', 'planet', 'attribute')],
                html.find_all('class', 'planetname', 'value'),
                collect_player()[0],
                collect_player()[1],
                collect_status()):

            class planet_class:
                position = const.coordinates(coordinates[0], coordinates[1], planet_pos)
                name = planet_name
                player = planet_player
                player_id = planet_player_id
                status = planet_status
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

    def fleet(self):
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
                html.find_all('id', 'fleet', 'attribute'),
                html.find_all('data-mission-type', '', 'attribute')[-missions:],
                html.find_all('data-return-flight', '', 'attribute')[-missions:],
                html.find_all('data-arrival-time', '', 'attribute')[0:missions],
                [html.find_all('href', '&componentgalaxy&galaxy', 'value')[i] for i in range(0, missions * 2, 2)],
                [html.find_all('href', '&componentgalaxy&galaxy', 'value')[i] for i in range(1, missions * 2, 2)]):

            class fleets_class:
                id = int(fleet_id.replace('fleet', ''))
                mission = int(fleet_mission)
                if fleet_returns == '1':
                    returns = True
                else:
                    returns = False
                arrival = datetime.fromtimestamp(int(fleet_arrival))
                origin = const.convert_to_coordinates(fleet_origin)
                destination = const.convert_to_coordinates(fleet_destination)
                list = [id, mission, returns, arrival, origin, destination]

            fleets.append(fleets_class)
        return fleets

    def phalanx(self, coordinates, id):
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
                    defences = spy_html.find_all('class', 'defense', 'attribute')
                    for defence in defences:
                        if defence != 'defense_imagefloat_left':
                            tech.append(const.convert_tech(int(defence.replace('defense', '')), 'defenses'))
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

    def do_research(self, research, id):
        OGame.build(self, research, id)

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
        self.session.put('https://lobby.ogame.gameforge.com/api/users/me/logout')
        return not OGame.is_logged_in(self)
