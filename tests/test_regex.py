# -*- coding: utf-8 -*-

from ogame import OGame

def test_get_planet_infos_regex_en():
    pyo = OGame('', '', '', auto_bootstrap=False)
    label = 'Homeworld [2:32:11]12.800km (0/188)-4°C to 36°COverviewResourcesResearchFacilitiesShipyardDefenceFleetGalaxy'
    infos = pyo.get_planet_infos_regex(label)
    assert 'Homeworld' == infos.group(1)
    assert '2' == infos.group(2)
    assert '32' == infos.group(3)
    assert '11' == infos.group(4)
    assert '12.800' == infos.group(5)
    assert '0' == infos.group(6)
    assert '188' == infos.group(7)
    assert '-4' == infos.group(8)
    assert '36' == infos.group(9)

def test_get_planet_infos_regex_german():
    pyo = OGame('', '', '', auto_bootstrap=False)
    label = 'Homeworld [2:32:11]12.800km (0/188)-4°C bis 36°COverviewResourcesResearchFacilitiesShipyardDefenceFleetGalaxy'
    infos = pyo.get_planet_infos_regex(label)
    assert 'Homeworld' == infos.group(1)
    assert '2' == infos.group(2)
    assert '32' == infos.group(3)
    assert '11' == infos.group(4)
    assert '12.800' == infos.group(5)
    assert '0' == infos.group(6)
    assert '188' == infos.group(7)
    assert '-4' == infos.group(8)
    assert '36' == infos.group(9)
