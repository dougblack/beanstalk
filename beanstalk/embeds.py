import re

from discord import Embed

from beanstalk.cached import FACTION_COLORS, FACTION_NAMES, PACKS, mwl, CYCLE_ROTATIONS


IMAGE_TEMPLATE = 'https://netrunnerdb.com/card_image/{code}.png'
CARD_VIEW_TEMPLATE = 'https://netrunnerdb.com/en/card/{code}'


SUBSTITUTIONS = {
    "(\[click\])": "<:nrclick:418454127488532480>",
    "(\[recurring-credit\])": "<:nrrecurringcredit:418457537881440256>",
    "(\[credit\])": "<:nrcredit:418453466826932229>",
    "(\[subroutine\])": "<:nrsubroutine:418457881222971403>",
    "(\[trash\])": "<:nrtrash:418457787689992193>",
    "(0\[mu\])": "<:nrmu0:418457664293568513>",
    "(1\[mu\])": "<:nrmu1:418457694354014228>",
    "(2\[mu\])": "<:nrmu2:418457723621867521>",
    "(3\[mu\])": "<:nrmu3:418457750906077184>",
}

class CardEmbed(object):
    def __init__(self, card):
        self.card = card
        self.embed = Embed(
            type='rich',
            title=card['title'],
            url=self.url(card),
        )

    def image(self, card):
        return card.get(
            'image_url',
            IMAGE_TEMPLATE.format(code=self.code)
        )

    def url(self, card):
        return CARD_VIEW_TEMPLATE.format(code=self.code)

    def __getattr__(self, attr):
        return self.card[attr]

    def has(self, name):
        return name in self.card


class CardImage(CardEmbed):
    def render(self):
        self.embed.set_image(url=self.image(self.card))
        return self.embed


class CardText(CardEmbed):
    def type_line(self):
        parts = [self.card['type_code'].title()]
        if self.has('keywords'):
            parts.append(': {}'.format(self.card['keywords']))

        type_code = self.type_code
        if type_code == 'program' and 'strength' not in self.card:
            type_code = 'weak_program'

        lines = {
            'identity': ['Deck: {minimum_deck_size}', 'Influence: {influence_limit}'],
            'agenda': ['Adv: {advancement_cost}', 'Score: {agenda_points}'],
            'ice': ['Rez: {cost}', 'Strength: {strength}', 'Influence: {faction_cost}'],
            'asset': ['Rez: {cost}', 'Trash: {trash_cost}', 'Influence: {faction_cost}'],
            'upgrade': ['Rez: {cost}', 'Trash: {trash_cost}', 'Influence: {faction_cost}'],
            'operation': ['Cost: {cost}', 'Influence: {faction_cost}'],
            'event': ['Cost: {cost}', 'Influence: {faction_cost}'],
            'program': ['Install: {cost}', 'μ: {memory_cost}', 'Strength {strength}', 'Influence: {faction_cost}'],
            'weak_program': ['Install: {cost}', 'μ: {memory_cost}', 'Influence: {faction_cost}'],
            'resource': ['Install: {cost}', 'Influence: {faction_cost}'],
            'hardware': ['Install: {cost}', 'Influence: {faction_cost}'],
        }

        parts.extend((' • ' + s).format(**self.card) for s in lines[type_code])
        return ''.join(parts)

    def transform_trace(self, re_obj):
        ss_conv = {
            '0': '⁰',
            '1': '¹',
            '2': '²',
            '3': '³',
            '4': '⁴',
            '5': '⁵',
            '6': '⁶',
            '7': '⁷',
            '8': '⁸',
            '9': '⁹',
        }
        ret_string = "**Trace"
        ret_string += ss_conv[re_obj.group(2)] + "** -"
        return ret_string

    def text_line(self):
        result = self.text
        for target, sub in SUBSTITUTIONS.items():
            result = re.sub(target, sub, result)
        result = re.sub("(<trace>Trace )(\d)(</trace>)", self.transform_trace, result, flags=re.I)
        return re.sub("(<strong>)(.*?)(</strong>)", "**\g<2>**", result)

    def influence_line(self):
        if self.has('neutral'):
            return ''

        result = '\n' + FACTION_NAMES[self.faction_code]
        if self.has('faction_cost'):
            result += ' ' + ('•' * self.faction_cost)
        return result


    def footer_line(self):
        parts = [
            FACTION_NAMES[self.faction_code],
            self.illustrator if self.has('illustrator') else 'No Illustrator',
        ]

        pack = PACKS[self.pack_code]
        rotated = CYCLE_ROTATIONS[pack['cycle_code']]

        parts.append('{} {}'.format(
            pack['name'] + (' (rotated)' if rotated else ''),
            self.position
        ))

        if self.code in mwl:
            mwl_name, mwl_effects = mwl[self.code]
            mwl_abbrev = mwl_name[-7:]
            mwl_effect = list(mwl_effects)[0]
            if mwl_effect in ('global_penalty', 'universal_faction_cost'):
                parts.append('{} Universal Influence ({})'.format(
                    mwl_effects[mwl_effect], mwl_abbrev,
                ))
            elif mwl_effect == 'is_restricted':
                parts.append('Restricted ({})'.format(
                    mwl_abbrev,
                ))
            elif mwl_effect == 'deck_limit' and mwl_effects[mwl_effect] == 0:
                parts.append('Banned ({})'.format(
                    mwl_abbrev,
                ))

        footer = ' • '.join(parts)
        return footer

    def render(self):
        self.embed.add_field(
            name=self.type_line(),
            value=self.text_line(),
        )
        self.embed.colour =  FACTION_COLORS[self.faction_code]
        self.embed.set_thumbnail(url=self.image(self.card))
        self.embed.set_footer(text=self.footer_line())
        return self.embed
