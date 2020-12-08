import requests
import configparser
from ogame import OGame
from ogame.constants import destination, coordinates, ships, mission, speed, buildings, status

# Read config file
config = configparser.ConfigParser()
config.read('config.cfg')
login = config['Login']
telegram = config['Telegram']


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
print('The sppe of the server is', server.Speed.universe)             
print('The Spped of the fleet is', server.Speed.fleet)                


class Telegram:
    def __init__(self):
        self.TOKEN = telegram.get('Token')
        self.CHAT = telegram.get('Chat')
        self.URL = "https://api.telegram.org/bot{}".format(self.TOKEN)

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def send_message(self, text):
        url = self.URL + "/sendMessage?text={}&chat_id={}".format(text, self.CHAT)
        self.get_url(url)

#Telegram informations
Telegram().send_message('---')
Telegram().send_message('Ogame bot ist gestartet. User {0} in the uni {1} was successfull logged in.'.format(login.get('Username'), login.get('Uni')))
if empire.characterclass():
  Telegram().send_message('The User has the class {0}'.format(empire.characterclass()))
if empire.planet_ids():
  for planetID, planetName in zip(empire.planet_ids(), empire.planet_names()):
    Telegram().send_message('The name of the planet is [{1}] with id [{0}]'.format(planetID, planetName))
