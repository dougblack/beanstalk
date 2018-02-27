import os
import re

from discord.ext import commands

TOKEN = os.environ.get('BEANSTALK_TOKEN')
CARD_PATTERN = re.compile('.*\[\[(.*)\]\].*')

bot = commands.Bot(command_prefix='!', description='Netrunner bot')

@bot.event
async def on_ready():
    print('Logged as {} with id {}.'.format(bot.user, bot.user.id))


@bot.event
async def on_message(message):
    matches = CARD_PATTERN.match(message.content)
    if not matches:
        return
    match = matches.group(1)
    await bot.send_message(message.channel, '{}, you say?'.format(match))


if __name__ == '__main__':
    bot.run(TOKEN)
