from ogame.constants import destination, coordinates, ships, mission, speed, buildings, resources, status, research

print('TEST OGAME FUNCTIONS')


def test(function, mandatory=False):
    if mandatory is not True:
        try:
            print(vars(function()))
        except TypeError:
            print(function())
    else:
        if function() is True:
            print(function())
        else:
            global succsess
            succsess = False
            raise Warning('funktion broke')


def pyogame(empire):
    succsess = True
    id = empire.planet_ids()[0]
    test(lambda: empire)
    test(lambda: empire.attacked())
    test(lambda: empire.neutral())
    test(lambda: empire.speed())
    test(lambda: empire.planet_ids())
    test(lambda: empire.planet_names())
    test(lambda: empire.id_by_planet_name(empire.planet_names()[0]))
    test(lambda: empire.moon_ids())
    test(lambda: empire.celestial_coordinates(id))
    test(lambda: empire.resources(id))
    test(lambda: empire.supply(id))
    test(lambda: empire.facilities(id))
    if empire.moon_ids():
        test(lambda: empire.moon_facilities(empire.moon_ids()[0]))
    test(lambda: empire.marketplace(id, 1))
    test(lambda: empire.buy_marketplace(12345, id))
    test(lambda: empire.submit_marketplace(resources(metal=100), resources(crystal=60), 10, id))
    test(lambda: empire.collect_marketplace())
    test(lambda: empire.research())
    test(lambda: empire.ships(id))
    test(lambda: empire.defences(id))
    test(lambda: empire.galaxy(coordinates(galaxy=1, system=1)))
    test(lambda: empire.ally())
    test(lambda: empire.fleet())
    # test(lambda: empire.phalanx(coordinates(1, 2, 3), empire.moon_ids()[0])) DANGERZONE IT GETS YOU BANNED WHEN INVALID
    test(lambda: empire.send_message(101175, 'Hallo'), True)
    test(lambda: empire.spyreports())
    test(lambda: empire.send_fleet(mission=mission.transport,
                                   id=id,
                                   where=empire.celestial_coordinates(empire.planet_ids()[1]),
                                   ships=[ships.large_transporter(1)]))
    test(lambda: empire.return_fleet(12345))
    test(lambda: empire.build(what=buildings.solar_satellite(1), id=id))
    test(lambda: empire.do_research(research=research.graviton, id=id))
    test(lambda: empire.collect_rubble_field(id=id))
    test(lambda: empire.is_logged_in())
    test(lambda: empire.logout())
    test(lambda: empire.relogin())
    test(lambda: empire.logout())

    if succsess is True:
        print('All test completed')
    else:
        raise BaseException('Test was not completed')

