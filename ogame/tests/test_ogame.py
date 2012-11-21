from unittest import TestCase
from nose.tools import raises
from mock import Mock, patch
from ogame import OGame
from ogame.errors import BAD_UNIVERSE_NAME
import ogame


class TestOGame(TestCase):

    @raises(BAD_UNIVERSE_NAME)
    def test_ogame_get_universe_url_raise_except_if_universe_does_not_exits(self):
        universe = 'DoesNotExists'
        OGame.SERVERS = {'asimpletest': 'url'}
        OGame.get_universe_url(universe)


    def test_ogame_get_universe_url_lower_name(self):
        universe = 'ASimpleTest'
        OGame.SERVERS = {'asimpletest': 'url'}
        url = OGame.get_universe_url(universe)
        self.assertEqual(url, 'url')
