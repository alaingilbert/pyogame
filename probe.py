from datetime import datetime
from ogame import OGame
import configparser
import time

from ogame.constants import coordinates, status, ships, mission

config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']
maxFleets = 5

# ogame
empire = OGame(login.get('Uni'), login.get('Username'), login.get('Password'))

# some vars
lastDateOfReport = datetime.now()
planetsToCheck = []
planetMILLET = empire.planet_ids()[0]
planetORTOVOS = empire.planet_ids()[1]

# get inactives players
galaxy_range = [3, 3] #[1, 6]
system_range = [140, 150] #[1, 499]
galaxy = galaxy_range[0]
system = system_range[0]
count = 1
while galaxy_range[0] <= galaxy <= galaxy_range[1]:
    while system_range[0] <= system <= system_range[1]:
        for planet in empire.galaxy(coordinates(galaxy, system)):
            if (status.inactive in planet.status) and not (status.vacation in planet.status):
                planetsToCheck.append(planet)
                print('#{3} at {2} has the status {1} and the name Planet {0}'.format(planet.name, planet.status, planet.position, count))
                count += 1
        system += 1
    galaxy += 1

print("Scan is finished")

# Send a spy probe to list
print()
for planet in planetsToCheck:
    # check if slot is free
    fleets = empire.fleet()
    send_fleets = 0
    for fleet in fleets:
        if fleet.list[1] == mission.spy:
            send_fleets += 1

    while send_fleets >= 5:
        time.sleep(10)
        print('Currently are 5 probs on the way. Wait 10 seconds..')
        fleets = empire.fleet()
        for fleet in fleets:
            if fleet.list[1] == mission.spy:
                send_fleets -= 1
        break

    # send 5 probes
    if empire.send_fleet(mission.spy, planetMILLET, planet.position, [ships.espionage_probe(2)]):
        fleets = empire.fleet()
        print('Mission SPYREPORT to {0} arrivas at {1}'.format(fleets[-1].destination, fleets[-1].arrival))


# print spy reports
print()
spyreports = sorted(empire.spyreports(lastDateOfReport=lastDateOfReport), key=lambda x: float(x.metal), reverse=True) #sort list descending
for spyreport in spyreports:
    print('{3}: Metal {0} Kristall {1} Deuterium {2} Defense {6}'
          .format(spyreport.metal if spyreport.metal != -1 else 'unbekannt',
                    spyreport.crystal if spyreport.crystal != -1 else 'unbekannt',
                    spyreport.deuterium if spyreport.deuterium != -1 else 'unbekannt',
                    spyreport.cords,
                    spyreport.planet,
                    spyreport.fright_date,
                    spyreport.defenseScore))

print('Probs finished!')