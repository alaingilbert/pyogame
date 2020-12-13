from datetime import datetime

from ogame import OGame
import configparser

from ogame.constants import coordinates, status, ships, mission

config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']

# ogame
empire = OGame(login.get('Uni'), login.get('Username'), login.get('Password'))

lastDateOfReport = datetime.now()

# # get inactives players
# galaxy_range = [1, 1] #[1, 6]
# system_range = [70, 71] #[1, 499]
# galaxy = galaxy_range[0]
# system = system_range[0]
# count = 1
# while galaxy_range[0] <= galaxy <= galaxy_range[1]:
#     while system_range[0] <= system <= system_range[1]:
#         for planet in empire.galaxy(coordinates(galaxy, system)):
#             if (status.inactive in planet.status) and not (status.vacation in planet.status):
#                 print('Nr. {3} at {2} has the status {1} and the name Planet {0}'.format(planet.name, planet.status, planet.position, count))
#                 count += 1
#         system += 1
#     galaxy += 1
#
# print("Scan is finished")

# # Send a Spyprobe to a random Player
# send_fleet = False
# while not send_fleet:
#     if empire.send_fleet(mission.spy, 33643513, [3, 162, 6, 1], [ships.espionage_probe(5)]):
#         send_fleet = True
#         break
#
# # Wait till Spyprobe arrives
# for fleet in empire.fleet():
#     if fleet.mission == mission.spy:
#         while datetime.now() < fleet.arrival:
#             continue


# print spy reports
spyreports = sorted(empire.spyreports(lastDateOfReport=lastDateOfReport, lastpage=3), key=lambda x: float(x.metal), reverse=True) #sort list descending
for spyreport in spyreports:
    print('{3}: Metal {0} Kristall {1} Deuterium {2} Defense {6}'
          .format(spyreport.metal if spyreport.metal != -1 else 'unbekannt',
                    spyreport.crystal if spyreport.crystal != -1 else 'unbekannt',
                    spyreport.deuterium if spyreport.deuterium != -1 else 'unbekannt',
                    spyreport.cords,
                    spyreport.planet,
                    spyreport.fright_date,
                    spyreport.defenseScore))

print('Finished!')