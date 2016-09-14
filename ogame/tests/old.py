from unittest import TestCase
# from nose.tools import raises
# from mock import Mock, patch
from ogame import OGame
# from ogame.errors import BAD_UNIVERSE_NAME
# import ogame
import datetime


class NewDatetime(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2012, 5, 5, 5, 5, 5)


class NewDate(datetime.date):
    @classmethod
    def today(cls):
        return cls(2012, 5, 5)


class FakeOGame(OGame):
    def __init__(self):
        pass


class TestOGame(TestCase):

    # @raises(BAD_UNIVERSE_NAME)
    def test_ogame_get_universe_url_raise_except_if_universe_does_not_exits(self):
        # universe = 'DoesNotExists'
        # OGame.SERVERS = {'asimpletest': 'url'}
        # OGame.get_universe_url(universe)
        pass

    def test_ogame_get_universe_url_lower_name(self):
        # universe = 'ASimpleTest'
        # OGame.SERVERS = {'asimpletest': 'url'}
        # url = OGame.get_universe_url(universe)
        # self.assertEqual(url, 'url')
        pass

    def test_get_datetime_from_time(self):
        fogame = FakeOGame()
        datetime.date = NewDate
        datetime.datetime = NewDatetime
        hour, minute, second = 6, 0, 0
        arrival_time = fogame.get_datetime_from_time(hour, minute, second)
        assert arrival_time.day == 5

    def test_get_datetime_from_time2(self):
        fogame = FakeOGame()
        datetime.date = NewDate
        datetime.datetime = NewDatetime
        hour, minute, second = 3, 0, 0
        arrival_time = fogame.get_datetime_from_time(hour, minute, second)
        assert arrival_time.day == 6
