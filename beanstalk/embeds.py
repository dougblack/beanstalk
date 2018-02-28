import re

from discord import Embed

from beanstalk.cached import FACTION_COLORS, FACTION_NAMES, PACK_NAMES, mwl


IMAGE_TEMPLATE = 'https://netrunnerdb.com/card_image/{code}.png'
CARD_VIEW_TEMPLATE = 'https://netrunnerdb.com/en/card/{code}'

class NREmbed(object):
    def __init__(self, card):
        self.card = card
        self.embed = Embed(
            type='rich',
            title=self.card['title'],
            url=self.url(card),
        )

    def image(self, card):
        return card.get(
            'image_url',
            IMAGE_TEMPLATE.format(code=self.card['code'])
        )

    def url(self, card):
        return CARD_VIEW_TEMPLATE.format(code=self.card['code'])


class ImageEmbed(NREmbed):
    def render(self):
        self.embed.set_image(url=self.image(self.card))
        return self.embed


class TextEmbed(NREmbed):
    def type_line(self):
        result = '{}'.format(self.card['type_code']).title()
        if 'keywords' in self.card:
            result += ': {}'.format(self.card['keywords'])

        if self.card['type_code'] == 'identity':
            result += ' • Deck: {}'.format(self.card['minimum_deck_size'])
            result += ' • Influence: {}'.format(self.card['influence_limit'])
        elif self.card['type_code'] == 'agenda':
            result += ' • Adv: {}'.format(self.card['advancement_cost'])
            result += ' • Score: {}'.format(self.card['agenda_points'])
        elif self.card['type_code'] == 'ice':
            result += ' • Rez: {}'.format(self.card['cost'])
            result += ' • Strength: {}'.format(self.card['strength'])
            result += ' • Influence: {}'.format(self.card['faction_cost'])
        else:
            cost_string = {
                'asset': 'Rez',
                'upgrade': 'Rez',
                'operation': 'Cost',
                'event': 'Cost',
                'program': 'Install',
                'resource': 'Install',
                'hardware': 'Install',
            }
            if 'cost' in self.card:
                result += ' • {}: {}'.format(cost_string[self.card['type_code']], self.card['cost'])
            if 'trash_cost' in self.card:
                result += ' • Trash: {}'.format(self.card['trash_cost'])
            if 'faction_cost' in self.card:
                result += ' • Influence: {}'.format(self.card['faction_cost'])
        return result

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
        result = re.sub("(\[click\])", "🕖", self.card['text'])
        result = re.sub("(\[recurring-credit\])", "💰⮐", result)
        result = re.sub("(\[credit\])", "💰", result)
        result = re.sub("(\[subroutine\])", "↳", result)
        result = re.sub("(\[trash\])", "🗑", result)
        result = re.sub("(\[mu\])", "μ", result)
        result = re.sub("(<trace>Trace )(\d)(</trace>)", self.transform_trace, result, flags=re.I)
        return re.sub("(<strong>)(.*?)(</strong>)", "**\g<2>**", result)

    def influence_line(self):
        if 'neutral' in self.card['faction_code']:
            return ''

        result = '\n' + FACTION_NAMES[self.card['faction_code']]
        if 'faction_cost' in self.card:
            result += ' ' + ('•' * self.card['faction_cost'])
        return result


    def footer_line(self):
        parts = [
            FACTION_NAMES[self.card['faction_code']],
            self.card['illustrator'] if 'illustrator' in self.card else 'No Illustrator',
            PACK_NAMES[self.card['pack_code']] + ' ' + str(self.card['position']),
        ]

        if self.card['code'] in mwl:
            value = mwl[self.card['code']]
            effect = value.keys()[0]
            if effect in ('global_penalty', 'universal_faction_cost'):
                parts += '{} Global Influence ({})'.format(
                    value[effect], value['name'][-7:]
                )
            elif effect == 'is_restricted':
                parts += 'Restricted ({})'.format(
                    value['name'][-7:]
                )
            elif effect == 'deck_limit':
                parts += 'Banned ({})'.format(
                    value['name'][-7:]
                )


        footer = ' • '.join(parts)
        return footer

    def render(self):
        self.embed.add_field(
            name=self.type_line(),
            value=self.text_line(),
        )
        self.embed.colour =  FACTION_COLORS[self.card['faction_code']]
        self.embed.set_thumbnail(url=self.image(self.card))
        self.embed.set_footer(text=self.footer_line())
        return self.embed
