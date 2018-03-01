import os
import json
import re

import time

from fuzzywuzzy import process
from discord.ext import commands
from discord import Embed

from beanstalk.embeds import CardImage, CardText
from beanstalk import cached
from beanstalk.cached import CARDS

TOKEN = os.environ.get('BEANSTALK_TOKEN')
CARD_PATTERN = re.compile('\[\[([^\]]*)\]\]')

bot = commands.Bot(command_prefix='!', description='Netrunner bot')

last_refresh = None


def choose_embed(match):
    if match.startswith('!'):
        embed = CardImage
        match = match[1:]
    else:
        embed = CardText
    return embed, match


@bot.event
async def on_ready():
    print('Logged in as {} with id {}.'.format(bot.user, bot.user.id))


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return

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

    await bot.process_commands(message)

@bot.group(pass_context=True)
async def beanstalk(ctx):
    pass


@beanstalk.command()
async def help(*_):
    await bot.say(
        '```Usage: \n' \
        '[[card]] - Fetch card embed.\n' \
        '[[!card]] - Fetch card image.\n' \
        '!beanstalk refresh - Refresh card cache.```'
    )


@beanstalk.command()
async def refresh(*_):
    global last_refresh
    if not last_refresh or time.time() - last_refresh > 300:
        cached.refresh()
        last_refresh = time.time()
        await bot.say('Cache refreshed.')
    else:
        await bot.say('Last refresh was only {} seconds ago. Skipping.'.format(
            int(time.time() - last_refresh)
        ))


if __name__ == '__main__':
    bot.run(TOKEN)
