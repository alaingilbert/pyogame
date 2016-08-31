class OGameException(Exception):
    pass


class BAD_CREDENTIALS(OGameException):
    pass


class BAD_UNIVERSE_NAME(OGameException):
    pass


class NOT_LOGGED(OGameException):
    pass


class CANT_PROCESS(OGameException):
    pass


class BAD_DEFENSE_ID(OGameException):
    pass


class BAD_SHIP_ID(OGameException):
    pass


class BAD_BUILDING_ID(OGameException):
    pass


class BAD_RESEARCH_ID(OGameException):
    pass
