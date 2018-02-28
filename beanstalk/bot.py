import os
import json
import re

from fuzzywuzzy import process
from discord.ext import commands
from discord import Embed

from beanstalk.embeds import CardImage, CardText
from beanstalk.cached import CARDS

TOKEN = os.environ.get('BEANSTALK_TOKEN')
CARD_PATTERN = re.compile('\[\[([^\]]*)\]\]')

bot = commands.Bot(command_prefix='!', description='Netrunner bot')


def choose_embed(match):
    if match.startswith('!'):
        embed = CardImage
        match = match[1:]
    else:
        embed = CardText
    return embed, match


@bot.event
async def on_ready():
    print('Logged as {} with id {}.'.format(bot.user, bot.user.id))


@bot.event
async def on_message(message):
    matches = set(re.findall(CARD_PATTERN, message.content))
    for match in matches:
        embed, match = choose_embed(match)

        try:
            target = process.extract(match, CARDS.keys(), limit=1)[0][0]
            card = CARDS[target]
        except Exception:
            await bot.send_message(message.channel, 'Unknown card')
            return

        embed = embed(card)
        await bot.send_message(message.channel, embed=embed.render())


if __name__ == '__main__':
    bot.run(TOKEN)
