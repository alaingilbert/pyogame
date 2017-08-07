# coding: utf-8

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
             'Deuteriumtank': 24,

             'Minedemétal': 1,
             'Minedecristal': 2,
             'Synthétiseurdedeutérium': 3,
             'Centraleélectriquesolaire': 4,
             'Hangardemétal': 22,
             'Hangardecristal': 23,
             'Réservoirdedeutérium': 24}

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
              'Ruimtewerf': 36,
              
              # FR
	      'Usinederobots': 14}


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
           'Interplanetaireraketten': 503,
           
           # FR
           'Lanceurdemissiles': 401,
           'Artillerielaserlégère': 402,
           'Artillerieàions': 405,
           'Artillerielaserlourde': 403}


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

         # NL
         'Kleinvrachtschip': 202,
         'Grootvrachtschip': 203,
         'Lichtgevechtsschip': 204,
         'Zwaargevechtsschip': 205,
         'Kruiser': 206,
         'Slagschip': 207,
         'Kolonisatiesschip': 208,
         'Recycler': 209,
         'Spionagesonde': 210,
         'Bommenwerper': 211,
         'Zonne-energiesatelliet': 212,
         'Vernietiger': 213,
         'Sterdesdoods': 214,
         'Interceptor': 215,

         # FR
         'Grandtransporteur': 203,
         'Vaisseaudecolonisation': 208,
         'Satellitesolaire': 212}

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
            'Gravitontechniek': 199,

            # FR
            'TechnologieOrdinateur': 108,
            'Astrophysique': 124,
            'TechnologieEspionnage': 106,
            'TechnologieBouclier': 111,
            'TechnologieProtectiondesvaisseauxspatiaux': 110}


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

Formules = {
        'batiments' : {
            'metal_mine': { 
                'cout': {
                    'Metal':[60,1.5], 'Crystal':[15,1.5], 'Deuterium':[0,0]
                },
                'production': [30,1.1],
                'consommation': [10,1.1],
            },
            'crystal_mine':{
                'cout': {
                    'Metal':[48, 1.6], 'Crystal':[24,1.6], 'Deuterium':[0,0]
                    },
                'production': [20,1.1],
                'consommation': [10,1.1],
            },
            'deuterium_synthesizer':{
                'cout': {
                    'Metal':[225,1.5], 'Crystal':[75,1.5], 'Deuterium':[0,0]
                    },
                'production': [10,1.1],
                'consommation': [20,1.1]
            },
        },
        'energy' : {
            'solar_plant':{
                'cout': {
                    'Metal':[75,1.5], 'Crystal':[30,1.5], 'Deuterium':[0,0]
                    },
                'production': [20,1.1],
                'consommation': [0,0]
            },
            'solar_satellite':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'production': [],
                'consommation': [0,0]
            },
            'fusion_reactor':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'production': [],
                'consommation': [10,1.1]
            },
        },
        'storage' :{
            'metal_storage':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
            'crystal_storage':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
            'deuterium_tank':{
                'cout': {
                    'Metal':[0,0], 'Crystal':[0,0], 'Deuterieum':[0,0]
                    },
                'capacite': [1.6],
                'consommation': [0,0]
            },
        },
        'facilities':{
            'RoboticsFactory' : {
                'cout' : {
                    'Metal':[400, 2], 'Crystal': [120,2], 'Deuterium': [200,2]
                    },
                'prerequis' : {
                },
            }
        }
    }
