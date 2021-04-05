import unittest
from random import randint
from ogame.constants import *


class UnittestOgame(unittest.TestCase):
    empire = None
    ids = []

    def collect_all_ids(self):
        self.ids.extend(self.empire.planet_ids())
        self.ids.extend(self.empire.moon_ids())

    def test_Vars(self):
        self.assertTrue(isinstance(self.empire.token, str))

    def test_Events(self):
        self.assertIsInstance(self.empire.attacked(), bool)
        self.assertIsInstance(self.empire.neutral(), bool)

    def test_Constants(self):
        speed = self.empire.server().Speed
        self.assertGreater(speed.universe, 0)
        self.assertGreater(speed.fleet, 0)

        self.assertIsInstance(self.empire.character_class(), str)

        self.assertIsInstance(self.empire.rank(), int)

        self.assertGreater(len(self.empire.planet_ids()), 0)
        planets_names = self.empire.planet_names()
        self.assertGreater(len(planets_names), 0)
        self.assertIsInstance(self.empire.id_by_planet_name(planets_names[0]), int)

        self.assertGreater(len(self.empire.moon_ids()), -1)
        self.assertGreater(len(self.empire.moon_names()), -1)

        self.collect_all_ids()

    def test_celestial(self):
        celestial = self.empire.celestial(id)
        self.assertGreater(celestial.diameter, 0)
        self.assertGreater(celestial.free, -1)
        self.assertIsInstance(celestial.temperature, list)

    def test_celestial_coordinates(self):
        for id in self.ids:
            celestial_coordinates = self.empire.celestial_coordinates(id)
            self.assertIsInstance(celestial_coordinates, list)
            self.assertEqual(len(celestial_coordinates), 4)

    def test_resources(self):
        for id in self.ids:
            res = self.empire.resources(id)
            self.assertIsInstance(res.resources, list)
            self.assertGreater(res.darkmatter, 0)
            self.assertIsInstance(res.energy, int)

    def test_supply(self):
        sup = self.empire.supply(self.empire.planet_ids()[0])
        self.assertTrue(0 < sup.metal_mine.level)

    def test_facilities(self):
        for id in self.empire.planet_ids():
            fac = self.empire.facilities(id)
            self.assertGreater(fac.robotics_factory.level, -1)

    def test_moon_facilities(self):
        for id in self.empire.moon_ids():
            fac = self.empire.moon_facilities(id)
            self.assertGreater(fac.robotics_factory.level, -1)

    def test_research(self):
        res = self.empire.research()
        self.assertGreater(res.energy.level, -1)

    def test_ships(self):
        ship = self.empire.ships(self.ids[0])
        self.assertGreater(ship.light_fighter.amount, -1)

    def test_defences(self):
        defence = self.empire.defences(self.ids[0])
        self.assertGreater(defence.rocket_launcher.amount, -1)

    def test_galaxy(self):
        for position in self.empire.galaxy(coordinates(1, 1)):
            self.assertIsInstance(position.player, str)
            self.assertIsInstance(position.list, list)
            self.assertIsInstance(position.moon, bool)

    def test_ally(self):
        self.assertIsInstance(self.empire.ally(), list)

    def test_fleet(self):
        for fleet in self.empire.fleet():
            self.assertIsInstance(fleet.id, int)

    def test_build(self):
        self.empire.build(
            what=buildings.crawler(5),
            id=self.empire.planet_ids()[0]
        )
        crawler = self.empire.supply(
            self.empire.planet_ids()[0]
        ).crawler.in_construction
        self.assertTrue(crawler.in_construction)

    def test_phalanx(self):
        Super_Dangereous_TO_test = 'You will get Banned'

    def test_send_message(self):
        send_message = False
        while not send_message:
            for position in self.empire.galaxy(coordinates(randint(1, 6), randint(1, 499))):
                if status.inactive in position.status:
                    send_message = self.empire.send_message(position.player_id, 'Hello')
                    break
        self.assertEqual(send_message, True)

    def test_spyreports(self):
        for report in self.empire.spyreports():
            self.assertIsInstance(report.fright, list)

    def test_send_fleet(self):
        for planet in self.empire.galaxy(
                coordinates(randint(1, 6), randint(1, 499))
        ):
            send = self.empire.send_fleet(
                mission.spy,
                self.ids[0],
                planet.position,
                [ships.espionage_probe(1)]
            )
            if send:
                self.assertEqual(send, True)
            else:
                self.empire.build(what=ships.espionage_probe(1), id=self.ids[0])
                self.assertIsInstance(send, bool)

    def relogin(self):
        self.empire.logout()
        self.empire.relogin()
        self.assertEqual(self.empire.is_logged_in(), True)

