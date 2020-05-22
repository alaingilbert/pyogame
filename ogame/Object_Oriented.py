try:
    import constants as const
except ImportError:
    import ogame.constants as const


def Object_Oriented(self):
    ogame = self

    class OO:
        def Planet(nr):
            id = ogame.planet_ids()[nr]
            supply = ogame.supply(id)
            facilities = ogame.facilities(id)
            defences = ogame.defences(id)

            class Planet:
                class Buildings:
                    class metal_mine:
                        level = supply.metal_mine.level
                        cost = supply.metal_mine.cost
                        is_possible = supply.metal_mine.is_possible
                        in_construction = supply.metal_mine.in_construction

                        def build(): return ogame.build(const.buildings.metal_mine, id)

                    class crystal_mine:
                        level = supply.crystal_mine.level
                        cost = supply.crystal_mine.cost
                        is_possible = supply.crystal_mine.is_possible
                        in_construction = supply.crystal_mine.in_construction

                        def build(): return ogame.build(const.buildings.crystal_mine, id)

                    class deuterium_mine:
                        level = supply.deuterium_mine.level
                        cost = supply.deuterium_mine.cost
                        is_possible = supply.deuterium_mine.is_possible
                        in_construction = supply.deuterium_mine.in_construction

                        def build(): return ogame.build(const.buildings.deuterium_mine, id)

                    class solar_plant:
                        level = supply.solar_plant.level
                        cost = supply.solar_plant.cost
                        is_possible = supply.solar_plant.is_possible
                        in_construction = supply.solar_plant.in_construction

                        def build(): return ogame.build(const.solar_plant.metal_mine, id)

                    class fusion_plant:
                        level = supply.fusion_plant.level
                        cost = supply.fusion_plant.cost
                        is_possible = supply.fusion_plant.is_possible
                        in_construction = supply.fusion_plant.in_construction

                        def build(): return ogame.build(const.buildings.fusion_plant, id)

                    class metal_storage:
                        level = supply.metal_storage.level
                        cost = supply.metal_storage.cost
                        is_possible = supply.metal_storage.is_possible
                        in_construction = supply.metal_storage.in_construction

                        def build(): return ogame.build(const.buildings.metal_storage, id)

                    class crystal_storage:
                        level = supply.crystal_storage.level
                        cost = supply.crystal_storage.cost
                        is_possible = supply.crystal_storage.is_possible
                        in_construction = supply.crystal_storage.in_construction

                        def build(): return ogame.build(const.buildings.crystal_storage, id)

                    class deuterium_storage:
                        level = supply.deuterium_storage.level
                        cost = supply.deuterium_storage.cost
                        is_possible = supply.deuterium_storage.is_possible
                        in_construction = supply.deuterium_storage.in_construction

                        def build(): return ogame.build(const.buildings.deuterium_storage, id)

                    class robotics_factory:
                        level = facilities.robotics_factory.level
                        cost = facilities.robotics_factory.cost
                        is_possible = facilities.robotics_factory.is_possible
                        in_construction = facilities.robotics_factory.in_construction

                        def build(): return ogame.build(const.buildings.robotics_factory, id)

                    class shipyard:
                        level = facilities.shipyard.level
                        cost = facilities.shipyard.cost
                        is_possible = facilities.shipyard.is_possible
                        in_construction = facilities.shipyard.in_construction

                        def build(): return ogame.build(const.buildings.shipyard, id)

                    class research_laboratory:
                        level = facilities.research_laboratory.level
                        cost = facilities.research_laboratory.cost
                        is_possible = facilities.research_laboratory.is_possible
                        in_construction = facilities.research_laboratory.in_construction

                        def build(): return ogame.build(const.buildings.research_laboratory, id)

                    class alliance_depot:
                        level = facilities.alliance_depot.level
                        cost = facilities.alliance_depot.cost
                        is_possible = facilities.alliance_depot.is_possible
                        in_construction = facilities.alliance_depot.in_construction

                        def build(): return ogame.build(const.buildings.alliance_depot, id)

                    class missile_silo:
                        level = facilities.missile_silo.level
                        cost = facilities.missile_silo.cost
                        is_possible = facilities.missile_silo.is_possible
                        in_construction = facilities.missile_silo.in_construction

                        def build(): return ogame.build(const.buildings.missile_silo, id)

                    class nanite_factory:
                        level = facilities.nanite_factory.level
                        cost = facilities.nanite_factory.cost
                        is_possible = facilities.nanite_factory.is_possible
                        in_construction = facilities.nanite_factory.in_construction

                        def build(): return ogame.build(const.buildings.nanite_factory, id)

                    class terraformer:
                        level = facilities.terraformer.level
                        cost = facilities.terraformer.cost
                        is_possible = facilities.terraformer.is_possible
                        in_construction = facilities.terraformer.in_construction

                        def build(): return ogame.build(const.buildings.terraformer, id)

                    class repair_dock:
                        level = facilities.repair_dock.level
                        cost = facilities.repair_dock.cost
                        is_possible = facilities.repair_dock.is_possible
                        in_construction = facilities.repair_dock.in_construction

                        def build(): return ogame.build(const.buildings.repair_dock, id)

                class Defences:
                    rocket_launcher = defences.rocket_launcher
                    laser_cannon_light = defences.laser_cannon_light
                    laser_cannon_heavy = defences.laser_cannon_heavy
                    gauss_cannon = defences.gauss_cannon
                    ion_cannon = defences.ion_cannon
                    plasma_cannon = defences.plasma_cannon
                    shield_dome_small = defences.shield_dome_small
                    shield_dome_large = defences.shield_dome_large
                    missile_interceptor = defences.missile_interceptor
                    missile_interplanetary = defences.missile_interplanetary

            return Planet

        def Moon(nr):
            id = ogame.moon_ids()[nr]
            facilities = ogame.moon_facilities(id)
            defences = ogame.defences(id)

            class Moon:
                class Buildings:
                    class robotics_factory:
                        level = facilities.robotics_factory.level
                        cost = facilities.robotics_factory.cost
                        is_possible = facilities.robotics_factory.is_possible
                        in_construction = facilities.robotics_factory.in_construction

                        def build(): return ogame.build(const.buildings.robotics_factory, id)

                    class shipyard:
                        level = facilities.shipyard.level
                        cost = facilities.shipyard.cost
                        is_possible = facilities.shipyard.is_possible
                        in_construction = facilities.shipyard.in_construction

                        def build(): return ogame.build(const.buildings.shipyard, id)

                    class moon_base:
                        level = facilities.moon_base.level
                        cost = facilities.moon_base.cost
                        is_possible = facilities.moon_base.is_possible
                        in_construction = facilities.moon_base.in_construction

                        def build(): return ogame.build(const.buildings.moon_base, id)

                    class sensor_phalanx:
                        level = facilities.sensor_phalanx.level
                        cost = facilities.sensor_phalanx.cost
                        is_possible = facilities.sensor_phalanx.is_possible
                        in_construction = facilities.sensor_phalanx.in_construction

                        def build(): return ogame.build(const.buildings.sensor_phalanx, id)

                        def scan(coordinates): return ogame.phalanx(coordinates, id)

                    class jump_gate:
                        level = facilities.jump_gate.level
                        cost = facilities.jump_gate.cost
                        is_possible = facilities.jump_gate.is_possible
                        in_construction = facilities.jump_gate.in_construction

                        def build(): return ogame.build(const.buildings.jump_gate, id)

                class Defences:
                    rocket_launcher = defences.rocket_launcher
                    laser_cannon_light = defences.laser_cannon_light
                    laser_cannon_heavy = defences.laser_cannon_heavy
                    gauss_cannon = defences.gauss_cannon
                    ion_cannon = defences.ion_cannon
                    plasma_cannon = defences.plasma_cannon
                    shield_dome_small = defences.shield_dome_small
                    shield_dome_large = defences.shield_dome_large
                    missile_interceptor = defences.missile_interceptor
                    missile_interplanetary = defences.missile_interplanetary

            return Moon

    return OO
