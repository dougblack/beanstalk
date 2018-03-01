from beanstalk.netrunner import (
    Cards,
    Factions,
    Packs,
    MWLs,
    Cycles,
)

CARDS = None
FACTION_COLORS = None
FACTION_NAMES = None
PACKS = None
CYCLE_ROTATIONS = None
MWL = None


def refresh():
    """
    Refresh the cache.
    """
    global CARDS
    global FACTION_COLORS
    global FACTION_NAMES
    global PACKS
    global CYCLE_ROTATIONS
    global MWL

    print('Refreshing cache')

    faction_resp = Factions().all()['data']
    card_resp = Cards().all()['data']
    pack_resp = Packs().all()['data']
    mwl_resp = MWLs().all()['data']
    cycle_resp = Cycles().all()['data']

    CARDS = {c['title']: c for c in card_resp}
    FACTION_COLORS = {f['code']: int(f['color'], 16) for f in faction_resp}
    FACTION_NAMES = {f['code']: f['name'] for f in faction_resp}
    PACKS = {p['code']: p for p in pack_resp}
    CYCLE_ROTATIONS = {c['code']: c['rotated'] for c in cycle_resp}
    MWL = {}

    for mwl_item in mwl_resp:
        for card_code, value in mwl_item['cards'].items():
            MWL[card_code] = (mwl_item['name'], value)

    print('Cache refreshed')

refresh()
