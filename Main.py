import logging
import discord
import names
from faker import Faker
import random
import mysql.connector

# all the objects needed
client = discord.Client()
fake = Faker()

# File logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a') # mode is append. r for read and w for write, r+ for both and w+ for both with resetting.
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    logger.info('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

# !help
    if message.content.startswith('!help'):
        with open('helpfile.txt') as f:
            await message.channel.send(f.read())

# !create
    if message.content.startswith('!create'):
        logger.info('{0} invoked !create command'.format(message.author))
        # PROFILE CREATION
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='password123', host='localhost', database='gamedata')
        cursor = cnx.cursor()

        #bquery = ("SELECT EXISTS(SELECT * FROM maintable WHERE discord_userID=%(discord_Uid)s)")
        query = ("SELECT * FROM gamedata WHERE discord_userID=%(discord_Uid)s)")
        userid = {'discord_Uid': message.author.id}

        cursor.execute(query, userid)

        if (cursor.rowcount == 0):
            print("Profile doesn't exist")
            #create the profile
        else:
            #for (name, age, discord_username) in cursor:
            #    print("A profile with name {}, aged {} by {} already exists".format(name, age, discord_username))
            print("Profile exists already. Use !profile command to see summary.")
        
# !profile
    if message.content.startswith('!profile'):
        # profile display
        logger.info('{0} invoked !profile command'.format(message.author))


# initialize the loop
client.run('{0}'.format(open('token.txt', 'r').read()))