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
CYCLES = None
MWL = None


def refresh():
    """
    Refresh the cache.
    """
    global CARDS
    global FACTION_COLORS
    global FACTION_NAMES
    global PACKS
    global CYCLES
    global MWL

    print('Rebuilding cache...')

    faction_resp = Factions().all()['data']
    card_resp = Cards().all()['data']
    pack_resp = Packs().all()['data']
    mwl_resp = MWLs().all()['data']
    cycle_resp = Cycles().all()['data']

    CARDS = {c['title']: c for c in card_resp}
    FACTION_COLORS = {f['code']: int(f['color'], 16) for f in faction_resp}
    FACTION_NAMES = {f['code']: f['name'] for f in faction_resp}
    PACKS = {p['code']: p for p in pack_resp}
    CYCLES = {c['code']: c for c in cycle_resp}
    MWL = {}

    latest_mwl = mwl_resp[-1]
    for card_code, value in latest_mwl['cards'].items():
        MWL[card_code] = (latest_mwl['name'], value)

    print('Cache rebuilt')

refresh()
