import logging
import discord
import names
from faker import Faker
import random
import mysql.connector

# Objects
client = discord.Client()
fake = Faker()

# File logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')  # mode is append. r for read and w for write, r+ for both and w+ for both with resetting.
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    logger.info('We have logged in as {0.user}'.format(client))

# Commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return

# !help
    if message.content.startswith('!help'):
        with open('helpfile.txt', 'r') as f:
            await message.channel.send(f.read())

# !create
    if message.content.startswith('!create'):
        logger.info('{0} invoked !create command'.format(message.author))

        # PROFILE CREATION

        # Connect to the database
        cnx = mysql.connector.connect(
            user='root', password='password123', host='localhost', database='gamedata')
        curA = cnx.cursor(buffered=True)

        # Get the record from the DB for message author
        query = (
            "SELECT * FROM gamedata.maintable WHERE discord_userID=%(discord_Uid)s")
        userid = {'discord_Uid': message.author.id}
        curA.execute(query, userid)

        # If user doesn't have exisiting profile
        if (curA.rowcount == -1):
            await message.channel.send("Profile doesn't exist.")
            add_profile = ("INSERT INTO gamedata.maintable "
                           "(discord_userID, discord_username, Name, Gender, Age, Occupation, Location, Happiness, Health, Smarts, Looks) "
                           "VALUES (%(did)s, %(dun)s, %(n)s, %(g)s, %(a)i, %(o)s, %(l)s, %(hap)f, %(hea)f, %(sma)f, %(loo)f) ")

            gender = random.choice(['male', 'female'])

            data_profile = {
                'did': message.author.id,
                'dun': message.author,
                'n': names.get_full_name(gender=gender),
                'g': gender,
                'a': 0,
                'o': 'None',
                'l': fake.address(),
                'hap': random.randrange(85, 101, 1),
                'hea': random.randrange(80, 101, 1),
                'sma': random.randrange(5, 97, 1),
                'loo': random.randrange(1, 101, 1)

                #bank = 0
                #bIsDead = False
            }
            
            curA.execute(add_profile, data_profile)
            # Save to DB and Close the cursor
            cnx.commit()
            await('Profile successfully created. use `!profile` to see details.')

        else:
            # Profile already exists
            #for (Name, Age, discord_username) in curA:
                # await message.channel.send("A profile with name {}, aged {} by {} already exists".format(
                #    Name, Age, discord_username))
                await message.channel.send("Profile already exists. Use `!profile` command to see summary.")

        curA.close()


# !profile
    if message.content.startswith('!profile'):
        # profile display
        logger.info('{0} invoked !profile command'.format(message.author))

# initialize the loop
client.run('{0}'.format(open('token.txt', 'r').read()))
