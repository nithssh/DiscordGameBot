################################################################################################################
# This file is the master and handles all the requests. The procedure definitions must be in a different file. #
################################################################################################################
import json
import logging

import discord

from responses import Response

ACCEPTED_COMMANDS = ('!help', '!create', '!surrender',
                     '!cancel_surrender', '!profile', '!age')

# Objects
client = discord.Client()

# File logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='front.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Database connection's config. Reads from a json file, converts to dict from obj.
# Reading config from json file instead of defining config(dict) in this code file.
with open('secrets/DB_login.json', 'r') as f:
    config = json.load(f)

# Events
@client.event
async def on_ready():
    print('Successfully logged in as {0}'.format(client.user))
    logger.info('Successfully logged in as {0}'.format(client.user))

# Commands
@client.event
async def on_message(message):

    # Respond only to messages in channels named "simulator" to avoid server wide spam.
    if (message.channel.name == 'simulator' or message.channel == "DMChannel"):
        if (not message.content.startswith(ACCEPTED_COMMANDS)):
            return

        # Don't process messages from the bot.
        if message.author == client.user:
            return
        else:
            # Variables used by all functions
            user_id = {'discord_Uid': message.author.id}

        # !help - send the help message from file.
        if message.content.startswith('!help'):
            logger.info('{0}, {1} invoked !help command.'.format(
                message.author.id, message.author))
            await Response.on_help(message)


        # !profile - send profile summary.
        if message.content.startswith('!profile'):
            logger.info('{0}, {1} invoked !profile command'.format(
                message.author.id, message.author))
            await Response.on_profile(message, user_id)

        # !surrender - delete current profile.
        if message.content.startswith('!surrender'):
            logger.info('{0}, {1} Invoked !surrender command'.format(
                message.author.id, message.author))
            await Response.on_surrender(message, user_id)

        # !cancel_surrender - cancel the profile deletion queuing.
        if (message.content.startswith('!cancel_surrender')):
            logger.info('The !cancel_deletion command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))
            await Response.on_cancel_surrender(message, user_id)

        # !age - increase the age of everyone in the world. [progresses the game]
        # toggles ready_to_age of the user, and triggers aging if everyone in world is ready.
        if (message.content.startswith('!age')):
            logger.info('The !age command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))
            await Response.on_age(message, user_id)

        # !create - create a new world.
        if message.content.startswith('!create'):
            logger.info('{0}, {1} invoked !create command'.format(
                message.author.id, message.author))
            await Response.on_create(message, client)
            
    # When the message isn't in a "simulator" channel.
    elif(message.content.startswith('!') and not
         (message.channel.name == 'Simulator' or message.channel.name == 'simulator')):

        logger.info('{0}, {1} used a command in the wrong channel in {2}'.format(
            message.author.id, message.author, message.guild.name))
        await message.channel.send('Command in wrong channel. '
                                   'Use the Simulator channel in order to avoid spam. Thanks!')

# initialize the loop
client.run('{0}'.format(open('secrets/botToken.txt', 'r').read()))
