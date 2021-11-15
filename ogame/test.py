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
        self.assertIsInstance(self.empire.friendly(), bool)

    def test_Constants(self):
        speed = self.empire.server().Speed
        self.assertGreater(speed.universe, 0)
        self.assertGreater(speed.fleet, 0)

        self.assertIsInstance(self.empire.character_class(), str)

        self.assertIsInstance(self.empire.rank(), int)

        self.assertGreater(len(self.empire.planet_ids()), 0)
        planets_names = self.empire.planet_names()
        self.assertGreater(len(planets_names), 0)
        self.assertIsInstance(
            self.empire.id_by_planet_name(planets_names[0]), int
        )

        self.assertGreater(len(self.empire.moon_ids()), -1)
        self.assertGreater(len(self.empire.moon_names()), -1)

        self.collect_all_ids()

        self.assertTrue(buildings.is_supplies(buildings.metal_mine))
        self.assertTrue(
            buildings.building_name(buildings.metal_mine) == 'metal_mine'
        )
        self.assertTrue(buildings.is_facilities(buildings.shipyard))
        self.assertTrue(buildings.is_defenses(buildings.rocket_launcher(10)))
        self.assertTrue(
            buildings.defense_name(
                buildings.rocket_launcher()
            ) == 'rocket_launcher'
        )
        self.assertTrue(research.is_research(research.energy))
        self.assertTrue(
            research.research_name(research.energy) == 'energy'
        )
        self.assertTrue(ships.is_ship(ships.small_transporter(99)))
        self.assertTrue(
            ships.ship_name(ships.light_fighter()) == 'light_fighter'
        )
        self.assertTrue(ships.ship_amount(ships.light_fighter(99)) == 99)
        self.assertEqual(resources(99, 99, 99), [99, 99, 99])
        self.assertEqual([3459, 864, 0], price(buildings.metal_mine, level=10))

    def test_slot_celestial(self):
        slot = self.empire.slot_celestial()
        self.assertGreater(slot.total, 0)

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

    def test_celestial_queue(self):
        for id in self.ids:
            celestial_queue = self.empire.celestial_queue(id)
            self.assertIsInstance(celestial_queue.list, list)

    def test_resources(self):
        for id in self.ids:
            res = self.empire.resources(id)
            self.assertIsInstance(res.resources, list)
            self.assertGreater(res.darkmatter, 0)
            self.assertIsInstance(res.energy, int)

    def test_resources_settings(self):
        settings = self.empire.resources_settings(
            self.ids[0],
            settings={buildings.metal_mine: speed.min}
        )
        self.assertEqual(settings.metal_mine, 10)
        settings = self.empire.resources_settings(
            self.ids[0],
            settings={buildings.metal_mine: speed.max}
        )
        self.assertEqual(settings.metal_mine, 100)

    def test_supply(self):
        sup = self.empire.supply(self.ids[0])
        self.assertTrue(0 < sup.metal_mine.level)

    def test_facilities(self):
        fac = self.empire.facilities(self.ids[0])
        self.assertTrue(0 < fac.robotics_factory.level)

    def test_moon_facilities(self):
        fac = self.empire.moon_facilities(self.ids[0])
        self.assertTrue(0 < fac.robotics_factory.level)

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

    def test_galaxy_debris(self):
        for position in self.empire.galaxy_debris(coordinates(1, 1)):
            self.assertIsInstance(position.position, list)
            self.assertIsInstance(position.has_debris, bool)
            self.assertIsInstance(position.metal, int)
            self.assertEqual(position.deuterium, 0)

    def test_ally(self):
        self.assertIsInstance(self.empire.ally(), list)

    def test_slot_fleet(self):
        slot = self.empire.slot_fleet()
        self.assertGreater(slot.fleet.total, 0)

    def test_fleet(self):
        UnittestOgame.test_send_fleet(self)
        for fleet in self.empire.fleet():
            self.assertIsInstance(fleet.id, int)
            if fleet.mission == mission.spy:
                self.assertTrue(fleet.mission == mission.spy)

    def test_return_fleet(self):
        UnittestOgame.test_send_fleet(self)
        for fleet in self.empire.fleet():
            if fleet.mission == mission.spy and not fleet.returns:
                fleet_returning = self.empire.return_fleet(fleet.id)
                self.assertTrue(fleet_returning)

    def test_build(self):
        before = self.empire.defences(
            self.ids[0]
        ).rocket_launcher.amount
        self.empire.build(
            what=buildings.rocket_launcher(),
            id=self.empire.planet_ids()[0]
        )
        after = self.empire.defences(
            self.ids[0]
        ).rocket_launcher
        self.assertTrue(before < after.amount or after.in_construction)

    def test_deconstruct_and_cancel(self):
        before = self.empire.supply(
            self.ids[0]
        ).metal_mine
        self.assertGreater(before.level, 0)
        self.assertFalse(before.in_construction)
        self.empire.deconstruct(
            what=buildings.metal_mine,
            id=self.ids[0]
        )
        after = self.empire.supply(
            self.ids[0]
        ).metal_mine
        self.assertTrue(before.level > after.level or after.in_construction)
        before = self.empire.supply(
            self.ids[0]
        ).metal_mine
        self.assertTrue(before.in_construction)
        self.empire.cancel_building(self.ids[0])
        after = self.empire.supply(
            self.ids[0]
        ).metal_mine
        self.assertFalse(after.in_construction)

    def test_phalanx(self):
        Super_Dangereous_TO_test = 'You will get Banned'

    def test_send_message(self):
        send_message = False
        while not send_message:
            for position in self.empire.galaxy(
                    coordinates(randint(1, 6), randint(1, 499))
            ):
                if status.inactive in position.status:
                    send_message = self.empire.send_message(
                        position.player_id,
                        'Hello'
                    )
                    break
        self.assertEqual(send_message, True)

    def test_spyreports(self):
        for report in self.empire.spyreports():
            self.assertIsInstance(report.name, str)
            self.assertIsInstance(report.position, list)
            self.assertIsInstance(report.metal, int)
            self.assertIsInstance(report.resources, list)
            self.assertIsInstance(report.fleet, dict)

    def test_send_fleet(self):
        espionage_probe = self.empire.ships(self.ids[0]).espionage_probe.amount
        if not 0 < espionage_probe:
            self.empire.build(ships.espionage_probe(), self.ids[0])
            while self.empire.ships(self.ids[0]).espionage_probe.amount <= 0:
                continue

        fleet_send = True
        while fleet_send:
            for planet in self.empire.galaxy(
                    coordinates(randint(1, 6), randint(1, 499))
            ):
                if status.inactive in planet.status \
                        and status.vacation not in planet.status:
                    fleet_send = not self.empire.send_fleet(
                        mission.spy,
                        self.ids[0],
                        where=planet.position,
                        ships=fleet(espionage_probe=1)
                    )
                    break
        self.assertTrue(not fleet_send)

    def test_collect_rubble_field(self):
        self.empire.collect_rubble_field(self.ids[0])

    def test_relogin(self):
        self.empire.logout()
        self.empire.relogin()
        self.assertTrue(self.empire.is_logged_in())

    def test_officers(self):
        officers = self.empire.officers()
        self.assertIsInstance(officers.commander, bool)
        self.assertIsInstance(officers.admiral, bool)
        self.assertIsInstance(officers.engineer, bool)
        self.assertIsInstance(officers.geologist, bool)
        self.assertIsInstance(officers.technocrat, bool)
