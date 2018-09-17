import os
import json
import re

import time

from fuzzywuzzy import process, fuzz
from discord.ext import commands
from discord import Embed

from beanstalk.embeds import CardImage, CardText
from beanstalk import cached
from beanstalk.cached import CARDS

TOKEN = os.environ.get('BEANSTALK_TOKEN')
QUERY_PATTERN = re.compile('\[\[([^\]]*)\]\]')

bot = commands.Bot(command_prefix='!', description='Netrunner bot')

last_refresh = None


@bot.group(pass_context=True)
async def beanstalk(ctx):
    """
    Creates a command group. !beanstalk <command> is the usage pattern
    for all beanstalk commands.
    """
    pass


@beanstalk.command()
async def help(*_):
    await bot.say(
        '```Usage: \n'
        '[[card]] - Fetch card embed.\n'
        '[[!card]] - Fetch card image.\n'
        '!beanstalk refresh - Refresh card cache.```'
    )


@beanstalk.command()
async def refresh(*_):
    """
    Refreshes the bots local cache of the card pool. Useful when
    the card pool expands.

    Must wait at least five minutes between cache refreshes.
    """
    global last_refresh
    time_since = time.time() - last_refresh if last_refresh else None
    if not time_since or time_since > 300:
        cached.refresh()
        last_refresh = time.time()
        from beanstalk.cached import CARDS
        await bot.say('Cache refreshed.')
    else:
        await bot.say(f'Last refresh was only {time_since} seconds ago. Skipping.')


@bot.event
async def on_ready():
    """
    Called once the bot is ready to receive and respond to messages.
    """
    print(f'Logged in as {bot.user} with id {bot.user.id}.')


def exact_match(query, cards):
    """
    Returns an embed if the query exactly matches a card name in the card set.

    We do this because the fuzzy searcher sometimes mis-scores these exact matches
    and hands back the wrong cards. This ensures that every card is fetchable via
    Beanstalk by using its exact name.
    """
    card = cards.get(query)
    if not card:
        return None
    return card


def fuzzy_match(query, cards):
    """
    Returns an embed if the query fuzzily matches a card name in the card set.

    The fuzzy searching library we use--`fuzzywuzzy`--scores its matches from 1
    to 100. Empirically, matches with scores less than 50 rarely look anything
    like the given query. So, we always use the top match and discard it if its
    score is less than 50 to prevent seemingly random responses from Beanstalk.
    """
    # Fuzzy match over the card pool.
    results = process.extract(query, cards.keys(), limit=1, scorer=fuzz.token_set_ratio)
    if not results:
        return None
    # If score is less than 50, ignore this result. Beanstalk will return no
    # embed in this case.
    card_name, score = results[0]
    if score < 50:
        return None
    return cards[card_name]


@bot.event
async def on_message(message):
    """
    Called on every message received by our bot.

    First, we pull out all queries (text wrapped in double square brackets
    `[[like this]]`) from the message.

    For each found query, we fuzzy match over the entire card pool which is
    locally cached in memory. If the highest scoring match has a score of 50 or
    greater (out of a possible score of 100), we embed it in either an
    `CardEmbed` or `ImageEmbed`, depending on if the original query was
    prefixed with `!` or not.

    After all this is done, we manually call `bot.process_commands` to give our
    `!beanstalk help` and `!beanstalk refresh` commands a chance to fire, as
    implementing `on_message` intercepts typical command processing.
    """

    # Ignore our own messages.
    if message.author.id == bot.user.id:
        return

    queries = set(re.findall(QUERY_PATTERN, message.clean_content))
    for query in queries:

        # Choose the embed.
        if query == '' or query == '!':
            continue
        elif query.startswith('!'):
            embed = CardImage
            query = query[1:]
        else:
            embed = CardText

        if not CARDS:
            await bot.send_message(message.channel, f'My card pool is empty. https://netrunnerdb.com might be down.')

        for search in (exact_match, fuzzy_match):
            card = search(query, CARDS)
            if card:
                embed = embed(card)
                print(f'{message.channel.id}: `{query}` satisifed with `{card["title"]}` via {search.__name__}')
                break

        if embed:
            await bot.send_message(message.channel, embed=embed.render())
        else:
            await bot.send_message(message.channel, f'No results for {query}')

    # Give other commands a chance to resolve.
    await bot.process_commands(message)


if __name__ == '__main__':
    bot.remove_command('help')
    bot.run(TOKEN)
