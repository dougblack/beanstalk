from beanstalk.netrunner import Cards, Factions, Packs

faction_resp = Factions().all()['data']
card_resp = Cards().all()['data']
pack_resp = Packs().all()['data']

CARDS = {c['title']: c for c in card_resp}
FACTION_COLORS = {f['code']: int(f['color'], 16) for f in faction_resp}
FACTION_NAMES = {f['code']: f['name'] for f in faction_resp}
PACK_NAMES = {p['code']: p['name'] for p in pack_resp}
