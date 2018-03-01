import re

from discord import Embed

from beanstalk.cached import (
    CYCLE_ROTATIONS,
    FACTION_COLORS,
    FACTION_NAMES,
    MWL,
    PACKS,
)


IMAGE_TEMPLATE = 'https://netrunnerdb.com/card_image/{code}.png'
CARD_VIEW_TEMPLATE = 'https://netrunnerdb.com/en/card/{code}'


class CardEmbed(object):
    """
    Represents an embed for a single card, to be rendered and returned.
    as a response to a search query.

    Crucially, and perhaps somewhat awkwardly, this class overrides
    `__getattr__` to forward missing attribute access to its card object. This
    little bit of magic makes card attribute accesses shorter and cleaner.  """

    def __init__(self, card):
        self.card = card

        # This is a discord.py Embed object, and is the thing we
        # will be building.
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
        """
        This allows code like `f = self.faction_cost` instead of
        `f = self.card['faction_cost']`.
        """
        return self.card[attr]

    def has(self, name):
        return name in self.card


class CardImage(CardEmbed):
    """
    Returns an embed with a full size card image.
    """
    def render(self):
        self.embed.set_image(url=self.image(self.card))
        return self.embed


class CardText(CardEmbed):
    """
    This is the default embed.

    This returns an embed with a textual representation of the card's text. It
    also includes a link to the card on NetrunnerDB as well as a thumbnail of
    the card image.
    """

    # These are substitutions applied to card text. The values
    # of this map point to Discord emojis.
    SUBSTITUTIONS = {
        "(\[click\])": "<:nrclick:418454127488532480>",
        "(\[recurring-credit\])": "<:nrrecurringcredit:418457537881440256>",
        "(\[credit\])": "<:nrcredit:418453466826932229>",
        "(\[subroutine\])": "↳",
        "(\[trash\])": "<:nrtrash:418457787689992193>",
        "(0\[mu\])": "<:nrmu0:418457664293568513>",
        "(1\[mu\])": "<:nrmu1:418457694354014228>",
        "(2\[mu\])": "<:nrmu2:418457723621867521>",
        "(3\[mu\])": "<:nrmu3:418457750906077184>",
    }

    def type_line(self):
        """
        Constructs a card's type line that contains both the card's
        type and subtypes, as well as costs to play it.

        Example:

        `Ice: Sentry - Tracer - Observer • Rez: 4 • Strength: 4 • Influence: 2`
        """
        parts = [self.card['type_code'].title()]
        if self.has('keywords'):
            parts.append(f': {self.card["keywords"]}')

        type_code = self.type_code
        if type_code == 'program' and 'strength' not in self.card:
            type_code = 'weak_program'
        elif type_code == 'identity' and 'base_link' in self.card:
            type_code = 'runner'

        lines = {
            'identity': ['Deck: {minimum_deck_size}', 'Influence: {influence_limit}'],
            'runner': ['Link: {base_link}', 'Deck: {minimum_deck_size}', 'Influence: {influence_limit}'],
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
        """
        Throws nice little superscripts on trace text for trace
        amounts.
        """
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
        """
        This transforms the text line to have all the fancy emojis in
        SUBSTITUTIONS, bolded text, and trace superscripts.
        """
        result = self.text
        for target, sub in self.SUBSTITUTIONS.items():
            result = re.sub(target, sub, result)
        result = re.sub("(<trace>Trace )(\d)(</trace>)", self.transform_trace, result, flags=re.I)
        return re.sub("(<strong>)(.*?)(</strong>)", "**\g<2>**", result)

    def footer_line(self):
        """
        This constructs the footer which contains faction membership, card
        illustrator, cycle membership and position, cycle rotations, and
        the latest MWL entry.

        Example:

        `Neutral • Meg Owenson • Data and Destiny 26 • Restricted (MWL 2.1)`
        """
        parts = [
            FACTION_NAMES[self.faction_code],
            self.illustrator if self.has('illustrator') else 'No Illustrator',
        ]

        pack = PACKS[self.pack_code]
        rotated = CYCLE_ROTATIONS[pack['cycle_code']]

        pack_text = pack['name'] + (' (rotated)' if rotated else ''),
        parts.append(f'{pack_text} {self.position}')

        if self.code in MWL:
            mwl_name, mwl_effects = MWL[self.code]
            mwl_abbrev = mwl_name[-7:]
            mwl_effect = list(mwl_effects)[0]
            if mwl_effect in ('global_penalty', 'universal_faction_cost'):
                effect_strength = mwl_effects[mwl_effect]
                parts.append(f'{effect_strength} Universal Influence ({mwl_abbrev})')
            elif mwl_effect == 'is_restricted':
                parts.append(f'Restricted ({mwl_abbrev})')
            elif mwl_effect == 'deck_limit' and mwl_effects[mwl_effect] == 0:
                parts.append(f'Banned ({mwl_abbrev})')

        footer = ' • '.join(parts)
        return footer

    def render(self):
        """
        Builds and returns self.embed.

        A call to self.embed.render() will serialize all of the content
        into a dict suitable to sending to Discord's API.
        """
        self.embed.add_field(
            name=self.type_line(),
            value=self.text_line(),
        )
        self.embed.colour =  FACTION_COLORS[self.faction_code]
        self.embed.set_thumbnail(url=self.image(self.card))
        self.embed.set_footer(text=self.footer_line())
        return self.embed
