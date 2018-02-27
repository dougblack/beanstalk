from beanstalk.netrunner import Cards, Factions

faction_resp = Factions().all()['data']
card_resp = Cards().all()['data']

CARDS = {c['title']: c for c in card_resp}
FACTION_COLORS = {f['code']: int(f['color'], 16) for f in faction_resp}
FACTION_NAMES = {f['code']: f['name'] for f in faction_resp}
