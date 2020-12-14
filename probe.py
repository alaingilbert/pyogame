from datetime import datetime

from ogame import OGame
import configparser
import time
from loguru import logger

from ogame.constants import coordinates, status, ships, mission

##################################
# credentials                    #
##################################
config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']
maxFleets = 5

# ogame
empire = OGame(login.get('Uni'), login.get('Username'), login.get('Password'))


##################################
# properties                     #
##################################
spyplanets = False
printreport = True
lastDateOfReport = datetime.now()
#lastDateOfReport = None
#lastPage = 30

galaxy_range = [2, 2] #[1, 6]
system_range = [75, 125] #[1, 499]

planetMILLET = empire.planet_ids()[0]
planetORTOVOX = empire.planet_ids()[1]
planetMAMMUT = empire.planet_ids()[2]
planetBase = planetMAMMUT

spyreportGalaxy = 2


##################################
# get inactive players           #
##################################
planetsToCheck = []
if spyplanets:
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

    print("Scans are finished")


##################################
# Send a spy probe to list         #
##################################
if spyplanets:
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
        if empire.send_fleet(mission.spy, planetBase, planet.position, [ships.espionage_probe(2)]):
            send_fleets += 1
            fleets = empire.fleet()
            print('Mission SPYREPORT to {0} arrivas at {1}'.format(fleets[send_fleets - 1].destination, fleets[send_fleets - 1].arrival))

    print("spys are finished")


##################################
# print spy reports              #
##################################
print()
spyreports = sorted(empire.spyreports(lastDateOfReport=lastDateOfReport, lastpage=30), key=lambda x: float(x.resourcesTotal), reverse=True) #sort list descending

#filter list
filteredReport = []
for spyreport in spyreports:
    if spyreport.cords.find('[' + str(spyreportGalaxy) + ':') != -1:
        filteredReport.append(spyreport)

for spyreport in filteredReport:
    message = '{3}: Total {7} Plunder {8} Metal {0} Crystal {1} Deuterium {2} Defense {6} ' \
              '=> You need {9} small transporters'\
                .format(
                    spyreport.metal if spyreport.metal != -1 else 'unknown',
                    spyreport.crystal if spyreport.crystal != -1 else 'unknown',
                    spyreport.deuterium if spyreport.deuterium != -1 else 'unknown',
                    spyreport.cords,
                    spyreport.planet,
                    spyreport.fright_date,
                    spyreport.defenseScore if spyreport.defenseScore != -1 else 'unknown',
                    spyreport.resourcesTotal,
                    spyreport.resourcesTotal / 2,
                    round(spyreport.resourcesTotal / 2 / 7500, 2)
                )

    # format output
    if spyreport.defenseScore == 0:
        logger.info(message)
    elif spyreport.defenseScore == -1:
        logger.error(message)
    elif spyreport.defenseScore > 0:
        logger.warning(message)

print('Probs finished!')