from enum import Enum

class buildings(Enum):
    METAL_MINE = 1
    CRYSTAL_MINE = 2
    DEUTERIUM_SYNTHESIZER = 3
    SOLAR_PLANT = 4
    FUSION_REACTOR = 12
    METAL_STORAGE = 22
    CRYSTAL_STORAGE = 23
    DEUTERIUM_TANK = 24
    SCHIELDED_METAL_DEN = 25
    UNDERGROUD_CRYSTAL_DEN = 26
    SEABED_DEUTERIUM_DEN = 27

class facilities(Enum):
    ALLIANCE_DEPOT = 34
    ROBOTICS_FACTORY = 14
    SHIPYARD = 21
    RESEARCH_LAB = 31
    MISSILE_SILO = 44
    NANITE_FACTORY = 15
    TERRAFORMER = 33
    SPACE_DOCK = 36

class defences(Enum):
    ROCKET_LAUNCHER = 401
    LIGHT_LASER = 402
    HEAVY_LASER = 403
    GAUSS_CANNON = 404
    ION_CANNON = 405
    PLASMA_TURRET = 406
    SMALL_SHIELD_DOME = 407
    LARGE_SHIELD_DOME = 408
    ANTI_BALLISTIC_MISSILES = 502
    INTERPLANETARY_MISSILES = 503

class ships(Enum):
    SMALL_CARGO = 202
    LARGE_CARGO = 203
    LIGHT_FIGHTER = 204
    HEAVY_FIGHTER = 205
    CRUISER = 206
    BATTLESHIP = 207
    COLONY_SHIP = 208
    RECYCLER = 209
    ESPIONAGE_PROBE = 210
    BOMBER = 211
    SOLAR_SATELLITE = 212
    DESTROYER = 213
    DEATHSTAR = 214
    BATTLECRUISER = 215

class researches(Enum):
    ESPIONAGE_TECHNOLOGY= 106
    COMPUTER_TECHNOLOGY= 108
    WEAPONS_TECHNOLOGY= 109
    SHIELDING_TECHNOLOGY= 110
    ARMOUR_TECHNOLOGY= 111
    ENERGY_TECHNOLOGY= 113
    HYPERSPACE_TECHNOLOGY= 114
    COMBUSTION_DRIVE= 115
    IMPULSE_DRIVE= 117
    HYPERSPACE_DRIVE= 118
    LASER_TECHNOLOGY= 120
    ION_TECHNOLOGY= 121
    PLASMA_TECHNOLOGY= 122
    INTERGALACTIC_RESEARCH_NETWORK= 123
    ASTROPHYSICS= 124
    GRAVITON_TECHNOLOGY= 199

class speeds(Enum):
    TEN_PERCENT = 1
    TWENTY_PERCENT = 2
    THIRTY_PERCENT = 3
    FORTY_PERCENT = 4
    FIFTY_PERCENT = 5
    SIXTY_PERCENT = 6
    SEVENTY_PERCENT = 7
    EIGHTY_PERCENT = 8
    NINETY_PERCENT = 9
    HUNDRED_PERCENT = 10

class missions(Enum):
    ATTACK = 1
    GROUPED_ATTACK = 2
    TRANSPORT = 3
    PARK = 4
    PARK_IN_THAT_ALLY = 5
    SPY = 6
    COLONIZE = 7
    RECYCLE_DEBRIS_FIELD = 8
    DESTROY = 9
    EXPEDITION = 15

Buildings = {'MetalMine': 1,
             'CrystalMine': 2,
             'DeuteriumSynthesizer': 3,
             'SolarPlant': 4,
             'FusionReactor': 12,
             'MetalStorage': 22,
             'CrystalStorage': 23,
             'DeuteriumTank': 24,
             'ShieldedMetalDen': 25,
             'UndergroundCrystalDen': 26,
             'SeabedDeuteriumDen': 27,

             # NL
             'Metaalmijn': 1,
             'Kristalmijn': 2,
             'Deuteriumfabriek': 3,
             'Zonne-energiecentrale': 4,
             'Fusiecentrale': 12,
             'Metaalopslag': 22,
             'Kristalopslag': 23,
             'Deuteriumtank': 24}


Facilities = {'AllianceDepot': 34,
              'RoboticsFactory': 14,
              'Shipyard': 21,
              'ResearchLab': 31,
              'MissileSilo': 44,
              'NaniteFactory': 15,
              'Terraformer': 33,
              'SpaceDock': 36,

              # NL
              'Alliantiehanger': 34,
              'Robotfabriek': 14,
              'Werf': 21,
              'Onderzoekslab': 31,
              'Raketsilo': 44,
              'Nanorobotfabriek': 15,
              'Terravormer': 33,
              'Ruimtewerf': 36}


Defense = {'RocketLauncher': 401,
           'LightLaser': 402,
           'HeavyLaser': 403,
           'GaussCannon': 404,
           'IonCannon': 405,
           'PlasmaTurret': 406,
           'SmallShieldDome': 407,
           'LargeShieldDome': 408,
           'AntiBallisticMissiles': 502,
           'InterplanetaryMissiles': 503,

           # NL
           'Raketlanceerder': 401,
           'Kleinelaser': 402,
           'Grotelaser': 403,
           'Gausskannon': 404,
           'Ionkannon': 405,
           'Plasmakannon': 406,
           'Kleineplanetaireschildkoepel': 407,
           'GroteplanetaireschildkoepelLargeShieldDome': 408,
           'Antiballistischeraketten': 502,
           'Interplanetaireraketten': 503}


Ships = {'SmallCargo': 202,
         'LargeCargo': 203,
         'LightFighter': 204,
         'HeavyFighter': 205,
         'Cruiser': 206,
         'Battleship': 207,
         'ColonyShip': 208,
         'Recycler': 209,
         'EspionageProbe': 210,
         'Bomber': 211,
         'SolarSatellite': 212,
         'Destroyer': 213,
         'Deathstar': 214,
         'Battlecruiser': 215,

         # FR
         'Petittransporteur': 202,
         'Grandtransporteur': 203,
         'Chasseurléger': 204,
         'Chasseurlourd': 205,
         'Croiseur': 206,
         'Vaisseaudebataille': 207,
         'Vaisseaudecolonisation': 208,
         'Recycleur': 209,
         'Sonded`espionnage': 210,
         'Bombardier': 211,
         'Satellitesolaire': 212,
         'Destructeur': 213,
         'Étoiledelamort': 214,
         'Traqueur': 215,

         # NL
         'Kleinvrachtschip': 202,
         'Grootvrachtschip': 203,
         'Lichtgevechtsschip': 204,
         'Zwaargevechtsschip': 205,
         'Kruiser': 206,
         'Slagschip': 207,
         'Kolonisatieschip': 208,
         'Recycler': 209,
         'Spionagesonde': 210,
         'Bommenwerper': 211,
         'Zonne-energiesatelliet': 212,
         'Vernietiger': 213,
         'Sterdesdoods': 214,
         'Interceptor': 215}


Research = {'EspionageTechnology': 106,
            'ComputerTechnology': 108,
            'WeaponsTechnology': 109,
            'ShieldingTechnology': 110,
            'ArmourTechnology': 111,
            'EnergyTechnology': 113,
            'HyperspaceTechnology': 114,
            'CombustionDrive': 115,
            'ImpulseDrive': 117,
            'HyperspaceDrive': 118,
            'LaserTechnology': 120,
            'IonTechnology': 121,
            'PlasmaTechnology': 122,
            'IntergalacticResearchNetwork': 123,
            'Astrophysics': 124,
            'GravitonTechnology': 199,

            # NL
            'Spionagetechniek': 106,
            'Computertechniek': 108,
            'Wapentechniek': 109,
            'Schildtechniek': 110,
            'Pantsertechniek': 111,
            'Energietechniek': 113,
            'Hyperruimtetechniek': 114,
            'Verbrandingsmotor': 115,
            'Impulsmotor': 117,
            'Hyperruimtemotor': 118,
            'Lasertechniek': 120,
            'Iontechniek': 121,
            'Plasmatechniek': 122,
            'IntergalactischOnderzoeksnetwerk': 123,
            'Astrofysica': 124,
            'Gravitontechniek': 199}


Speed = {'10%': 1,
         '20%': 2,
         '30%': 3,
         '40%': 4,
         '50%': 5,
         '60%': 6,
         '70%': 7,
         '80%': 8,
         '90%': 9,
         '100%': 10}


Missions = {'Attack': 1,
            'GroupedAttack': 2,
            'Transport': 3,
            'Park': 4,
            'ParkInThatAlly': 5,
            'Spy': 6,
            'Colonize': 7,
            'RecycleDebrisField': 8,
            'Destroy': 9,
            'Expedition': 15}
