import configparser
from ogame import OGame
from core.telegram import Telegram

# Read config file
config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']
telegramKey = config['Telegram']

# Inits
print('### Init service start')
telegram = Telegram(telegramKey.get('Token'), telegramKey.get('Chat'))
print('Telegram service is started')

# block: user infos
print('### User informations')
empire = OGame(login.get('Uni'), login.get('Username'), login.get('Password'))
print('User {0} in the uni {1} was successfull logged in'.format(login.get('Username'), login.get('Uni')))
print('The User has the class', empire.characterclass())
if empire.planet_ids():
  for planetID, planetName in zip(empire.planet_ids(), empire.planet_names()):
    print('The name of the planet is [{1}] with id [{0}]'.format(planetID, planetName))
print('')


# block: server stats
print('### Some informations about the server')
server = empire.server()
print('The server version is', server.version)                    
print('The speed of the server is', server.Speed.universe)
print('The speed of the fleet is', server.Speed.fleet)

# block: probe
print('### Run probe')
# Send a Spyprobe to a random Player




#telegram informations
telegram.send_message('---')
telegram.send_message('Ogame bot ist gestartet. User {0} in the uni {1} was successfull logged in.'.format(login.get('Username'), login.get('Uni')))
if not empire.characterclass():
  telegram.send_message('The User has the class {0}'.format(empire.characterclass()))
if empire.planet_ids():
  for planetID, planetName in zip(empire.planet_ids(), empire.planet_names()):
    telegram.send_message('The name of the planet is [{1}] with id [{0}]'.format(planetID, planetName))
