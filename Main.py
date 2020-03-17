import json
import logging
import random
import threading

import discord
import mysql.connector
import names
from faker import Faker

# Objects
client = discord.Client()
fake = Faker()

# File logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
# Current mode is a = append. r for read, w for write, r+ for both and w+ for both with resetting.
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Database connection's config. Reads from a json file, converts to dict from obj. 
# Reading config from json file instead of defining config(dict) in this code file.
with open('keys/DB_login.json', 'r') as f:
    config = json.load(f)

def bExists(authorID):
    """This fuction check if a user profile exists.\n
    Should be used before proceeding with a command.\n
    Returns: True if user profile exists in gamedata.maintable\n
             False if profile doesn't exist in the same."""

    ID = {
        'user_id': authorID
    }
    # connect to database
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(buffered=True)

    # Get the record from the DB for message author
    query = (
        "SELECT * FROM gamedata.maintable WHERE discord_userID=%(user_id)s")
    cursor.execute(query, ID)

    # If user doesn't have exisiting profile
    if (cursor.rowcount == 0):
        result = False
    else:
        result = True

    return result

# Events
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    logger.info('We have logged in as {0.user}'.format(client))

# Commands
@client.event
async def on_message(message):
    if ((message.channel.name == 'Simulator' or message.channel.name == 'simulator') and message.content.startswith('!')):
            
        # Prevents recursion
        if message.author == client.user: 
            return

        # !help
        if message.content.startswith('!help'):
            logger.info('{0}, {1} invoked !help command.'.format(message.author.id, message.author))
            with open('message_templates/help_message.txt', 'r') as f:
                await message.channel.send(f.read())

        # !create
        if message.content.startswith('!create'):
            logger.info('{0}, {1} invoked !create command'.format(
                message.author.id, message.author))

            # If user doesn't have exisiting profile
            if (bExists(message.author.id) == False):
                
                await message.channel.send("Profile doesn't exist.")

                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=True)

                add_profile = ("INSERT INTO gamedata.maintable "
                            "(discord_userID, discord_username, Name, Gender, Age, Occupation, Location, Happiness, Health, Smarts, Looks, Schedule_deletion, Bank) "
                            "VALUES (%(did)s, %(dun)s, %(n)s, %(g)s, %(a)s, %(o)s, %(l)s, %(hap)s, %(hea)s, %(sma)s, %(loo)s, %(del)s, %(bnk)s )")

                gender = random.choice(['male', 'female'])
                data_profile = {
                    'did': message.author.id,
                    'dun': message.author.display_name,
                    'n': names.get_full_name(gender=gender),
                    'g': gender,
                    'a': 0,
                    'o': 'None',
                    'l': fake.address(),
                    'hap': random.randrange(85, 101, 1),
                    'hea': random.randrange(80, 101, 1),
                    'sma': random.randrange(5, 97, 1),
                    'loo': random.randrange(1, 101, 1),
                    'del': 0,
                    'bnk': 0
                }

                try:
                    cursor.execute(add_profile, data_profile)
                    # Save to DB and Close the cursor
                    cnx.commit()
                    await message.channel.send('Profile successfully created. use `!profile` to see details.')
                    logger.info("{0}, {1} profile creation successful.".format(message.author.id, message.author))

                except:
                    cnx.rollback()
                    await message.channel.send('Profile creation failed.')
                    logger.error("{0}, {1} profile creation failed".format(message.author.id, message.author))
                    
            else:
                # Profile already exists
                await message.channel.send("Profile already exists. Use `!profile` command to see summary.")
                logger.info("{0}, {1} profile already exists.".format(message.author.id, message.author))

            # Close
            cursor.close()
            cnx.close()


        # !profile
        if message.content.startswith('!profile'):
            logger.info('{0}, {1} invoked !profile command'.format(message.author.id, message.author))
            
            if (bExists(message.author.id)):
                
                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=False)
                userid = {'discord_Uid': message.author.id}
            
                # Retrive the record from the DB
                query = ("SELECT * FROM gamedata.maintable "
                        "WHERE discord_userID=%(discord_Uid)s")
                cursor.execute(query, userid)
                record = cursor.fetchall()

                # Ready the data for next operations.
                for row in record:
                    logger.info('row from record loaded.')

                # Load the message from the file
                with open('message_templates/profile_summary.txt', 'r') as f:
                    profile_message = f.read().format(row[2],row[4],row[3],row[5],row[6],row[7],row[8],row[9],row[10],row[12])
                
                # Send the summary message using data from the dict
                await message.channel.send(profile_message)

                # Close 
                cursor.close()
                cnx.close()

            else:
                await message.channel.send("@{0}'s profile doesnt exist. Invoke `!help` to get started.".format(message.author))
                logger.info("{0}, {1} profile doesn't exist doesn't to summarize.".format(message.author.id, message.author))

        # !surrender
        if message.content.startswith('!surrender'):
            # profile deletion
            logger.info('{0}, {1} Invoked !surrender command'.format(
                message.author.id, message.author))

            if(bExists(message.author.id)):

                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=True)
                userid = {'discord_Uid': message.author.id}

                # UPDATE the schedule_deletion field to 1 (true).
                update_deletion = ("UPDATE gamedata.maintable "
                                "SET Schedule_deletion = '1' "
                                "WHERE discord_userID=%(discord_Uid)s")
                cursor.execute(update_deletion, userid)
                cnx.commit()

                # The Function that gets called after 2 mins.
                def deletion_function():

                    # Retrive updated record
                    schedule_deletion_query = (
                        "SELECT Schedule_deletion FROM gamedata.maintable WHERE discord_userID=%(discord_Uid)s")
                    userid = {'discord_Uid': message.author.id}
                    cursor.execute(schedule_deletion_query, userid)

                    for Schedule_deletion in cursor:
                        bDeletion = Schedule_deletion

                    if (bDeletion[0] == 1):
                        # Procede with deletion.
                        delete_query = ("DELETE FROM gamedata.maintable "
                                        "WHERE discord_userID=%(discord_Uid)s")
                        try:
                            cursor.execute(delete_query, userid)
                            cnx.commit()
                            logger.info('{0}, {1} profile was successfully deleted.'.format(
                                message.author.id, message.author))

                            # Close
                            cursor.close()
                            cnx.close()
                            # await message.channel.send('@{0} profile was successfully deleted.'.format(message.author))

                        except:
                            cnx.rollback()
                            logger.error("{0}, {1}'s profile was not deleted due to an error.".format(message.author.id, message.author))

                            # Close
                            cursor.close()
                            cnx.close()
                            # await message.channel.send('@{0} profile was not deleted due to an error. Sorry!'.format(message.author))
                    else:
                        # The deletion has been cancelled
                        logger.info('The deletion of {0}, {1} profile has been cancelled'.format(
                            message.author, message.author.id))

                # start the timer
                timer = threading.Timer(120.0, deletion_function)
                await message.channel.send('The profile will be deleted after 2 mins,\nUse the `!cancel_surrender` command to ABORT the deletion.')
                timer.start()
                logger.info('Deletion timer started for {0}, {1}'.format(message.author, message.author.id))
                    
            else:
                await message.channel.send("@{0} 's profile doesn't exist to delete. Invoke `!help` to see help.".format(message.author))
                logger.info("{0}, {1} profile doesn't exist to delete. [from:!surrender]")


        # !cancel_surrender
        if (message.content.startswith('!cancel_surrender')):
            logger.info('The !cancel_deletion command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))
            
            if (bExists(message.author.id)):
            
                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=True)
                userid = {'discord_Uid': message.author.id}

                # UPDATE the schedule_deletion field to 0 (False).
                update_deletion = ("UPDATE gamedata.maintable "
                                "SET Schedule_deletion = '0' "
                                "WHERE discord_userID=%(discord_Uid)s")
                try:
                    cursor.execute(update_deletion, userid)
                    cnx.commit()
                    logger.info('The !cancel_surrender command has been successfully executed for {0}, {1}'.format(
                        message.author, message.author.id))
                    await message.channel.send('The profile deletion (surrender) has been successfully ABORTED.\nYou can continue playing without any change.')
                except:
                    logger.error('There was an error in executing the !cancel_surrender command for {0}, {1}'.format(
                        message.author, message.author.id))
                    await message.channel.send("There was an error in cancelling the deletion.")

                # Close
                cursor.close()
                cnx.close()
            else:
                await message.channel.send("@{0} 's profile doesn't exist. Invoke `!help` to see help.".format(message.author))
                logger.info("{0}, {1} profile doesn't exist. [from:!cancel_surrender]")
    
    elif(message.content.startswith('!') and not (message.channel.name == 'Simulator' or message.channel.name == 'simulator')):
        logger.info('{0}, {1} used a command in the wrong channel in {2}'.format(message.author.id, message.author, message.guild.name))
        await message.channel.send('Command in wrong channel. Use the Simulator channel in order to avoid spam. Thanks!')

# initialize the loop
client.run('{0}'.format(open('keys/token.txt', 'r').read()))
