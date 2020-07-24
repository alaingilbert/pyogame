from __init__ import OGame

empire = OGame('Indus', 'marcos.gam7@gmail.com', 'MarcosDaniel')

ids = empire.planet_ids()
print(empire.defences(ids[0]).rocket_launcher.amount)
