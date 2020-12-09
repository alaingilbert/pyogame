from ogame import OGame
import configparser

from ogame.constants import coordinates, status

config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']

# ogame
empire = OGame(login.get('Uni'), login.get('Username'), login.get('Password'))

# probe

galaxy = 1
count = 1
while galaxy <= 6:
    system = 1
    while system <= 499:
        for planet in empire.galaxy(coordinates(galaxy, system)):
            if (status.inactive in planet.status) and not (status.vacation in planet.status):
                print('Nr. {3} at {2} has the status {1} and the name Planet {0}'.format(planet.name, planet.status, planet.position, count))
                count += 1
        system += 1
    galaxy += 1
