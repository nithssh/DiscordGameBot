import json
import logging
import random
import threading

import discord
import mysql.connector
import names
from faker import Faker

import utilities
from aging import Aging

# Objects
client = discord.Client()
fake = Faker()

# File logger
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
# Current mode is 'a' = append. 'r' for read, 'w' for write, 'r+' for both and 'w+' for both with resetting.
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Database connection's config. Reads from a json file, converts to dict from obj. 
# Reading config from json file instead of defining config(dict) in this code file.
with open('keys/DB_login.json', 'r') as f:
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
    if ((message.channel.name == 'simulator' and message.content.startswith('!')) or (message.channel == "DMChannel" and message.content.startswith('!'))):
            
        # Don't process messages from the bot. [anti-recursion]
        if message.author == client.user: 
            return

        # !help - send the help message from file.
        if message.content.startswith('!help'):
            logger.info('{0}, {1} invoked !help command.'.format(message.author.id, message.author))
            with open('message_templates/help_message.txt', 'r') as f:
                await message.channel.send(f.read())

        # !create - create a new world.
        if message.content.startswith('!create'):
            logger.info('{0}, {1} invoked !create command'.format(
                message.author.id, message.author))

            # If user doesn't have exisiting profile
            if (utilities.b_exists(message.author.id) == False):
                
                await message.channel.send("Profile doesn't exist.")

                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=False)

                add_profile = ("INSERT INTO gamedata.maintable "
                                "(discord_userID, discord_username, World_ID, Name, Gender, Age, Occupation, Location, Happiness, Health, Smarts, Looks, Schedule_deletion, Bank) "
                                "VALUES (%(did)s, %(dun)s, %(wor)s, %(n)s, %(g)s, %(a)s, %(o)s, %(l)s, %(hap)s, %(hea)s, %(sma)s, %(loo)s, %(del)s, %(bnk)s )")

                # Generate World_ID. Retrive the last value of world_id and increment
                get_max_world_id = ("SELECT World_ID FROM gamedata.maintable ORDER BY World_ID DESC LIMIT 1")
                cursor.execute(get_max_world_id)
                max_world_id = cursor.fetchall()
                if (len(max_world_id) != 0):
                    generated_world_id = 1
                    generated_world_id +=  max(max_world_id[0])
                else:
                    generated_world_id = 1

                # Parse the message into its sub components to use in world creation
                message_parts = utilities.parse_message(message, '!create')

                for part in message_parts:
                    try:
                        username = part.split('#')
                        user_id = discord.utils.get(client.get_all_members(), name=username[0], discriminator=username[1]).id
                        gender = random.choice(['male', 'female'])

                        data_profile = {
                            'did': user_id,
                            'dun': username[0],
                            'wor': generated_world_id,
                            'n': names.get_full_name(gender=gender),
                            'g': gender,
                            'a': 0,
                            'o': 'None',
                            'l': fake.address(),
                            'hap': random.randrange(90, 101, 1),
                            'hea': random.randrange(90, 101, 1),
                            'sma': random.randrange(5, 97, 1),
                            'loo': random.randrange(5, 101, 1),
                            'del': 0,
                            'bnk': 0
                            }
                    
                        cursor.execute(add_profile, data_profile)
                        # Save to DB
                        cnx.commit()
                        await message.channel.send('Profile successfully created. use `!profile` to see details.')
                        logger.info("{0}, {1} profile creation successful.".format(user_id, username[0]))

                    except:
                        cnx.rollback()
                        await message.channel.send('Profile creation failed. This is most probably due to incorrect command arguments. See `!help` to find correct usage.')
                        logger.error("{0}, {1} profile creation failed".format(message.author.id, message.author))
            
                # Close the DB connection
                cursor.close()
                cnx.close()  

            else:
                # Profile already exists
                await message.channel.send("Profile already exists. Players can have only one profile at a time. Use `!profile` command to see summary. Use !surrender command to delete profile to create new one in a new world.")
                logger.info("{0}, {1} profile already exists.".format(message.author.id, message.author))

        # !profile - send profile summary.
        if message.content.startswith('!profile'):
            logger.info('{0}, {1} invoked !profile command'.format(message.author.id, message.author))
            
            if (utilities.b_exists(message.author.id)):
                
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
                    profile_message = f.read().format(row[3],row[5],row[4],row[6],row[7],row[8],row[9],row[10],row[11],row[13],row[2],row[1])
                
                # Send the summary message using data from the dict
                await message.channel.send(profile_message)

                # Close 
                cursor.close()
                cnx.close()

            else:
                await message.channel.send("@{0}'s profile doesn't exist. Invoke `!help` to get started.".format(message.author))
                logger.info("{0}, {1} profile doesn't exist doesn't to summarize.".format(message.author.id, message.author))

        # !surrender - delete current profile.
        if message.content.startswith('!surrender'):
            # profile deletion
            logger.info('{0}, {1} Invoked !surrender command'.format(
                message.author.id, message.author))

            if(utilities.b_exists(message.author.id)):

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

        # !cancel_surrender - cancel the profile deletion queuing.
        if (message.content.startswith('!cancel_surrender')):
            logger.info('The !cancel_deletion command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))
            
            if (utilities.b_exists(message.author.id)):
            
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
        
        # !age - increase the age of everyone in the world. [progress the game]
        # toggles ready_to_age of the user, and triggers aging if everyone in world is ready.
        if (message.content.startswith('!age')):
            logger.info('The !age command has been invoked by {0}, {1}'.format(message.author, message.author.id))
            
            if(utilities.b_exists(message.author.id)):
                
                # Connect to the database
                cnx = mysql.connector.connect(**config)
                cursor = cnx.cursor(buffered=False)
                userid = {'discord_Uid': message.author.id}

                # get current value of ready_to_age of user
                get_aging_status = ("SELECT ready_to_age FROM gamedata.maintable "
                                    "WHERE discord_userID = %(discord_Uid)s")
                cursor.execute(get_aging_status, userid)
                current_aging_status = cursor.fetchall()

                update_aging_status = ("UPDATE gamedata.maintable "
                                        "SET ready_to_age = %(aging_status)s "
                                        "WHERE discord_userID = %(discord_Uid)s")
                
                # Toggle the ready_to_age field of user
                if (current_aging_status[0] == 1):
                    new_aging_status_data = {
                        'aging_status': 0,
                        'discord_Uid': message.author.id
                    }
                    cursor.execute(update_aging_status, new_aging_status_data)
                    cnx.commit()
                else:
                    new_aging_status_data = {
                        'aging_status': 1,
                        'discord_Uid': message.author.id
                    }
                    cursor.execute(update_aging_status, new_aging_status_data)
                    cnx.commit()

                # Check if all profiles in world are ready
                
                # Get the world_id of the world to be aged up
                get_world_id = ("SELECT World_ID FROM gamedata.maintable "
                                "WHERE discord_userID = %(discord_Uid)s")
                cursor.execute(get_world_id, userid)
                world_id = cursor.fetchall()
                
                # load the current ready_to_age of all the users in the world
                get_ready_status_query = ("SELECT ready_to_age FROM gamedata.maintable "
                                          "WHERE World_ID = %s")
                cursor.execute(get_ready_status_query, world_id[0])
                current_ready_status_data = cursor.fetchall()
                
                sum_ready_to_age = 0
                for status in current_ready_status_data:
                    sum_ready_to_age += status[0]
                
                # if all true
                if (sum_ready_to_age/len(current_ready_status_data) == 1):
                    ager = Aging()
                    ager.age_up(message)
                    await message.channel.send('A year has passed in the World. Everyone is a year older.')
                else:
                    # For pretty printing the message for user. Changes aging_status to True or False (which is user-readable format)
                    if(new_aging_status_data['aging_status'] == 1):
                        toggle = True
                    else:
                        toggle = False
                    await message.channel.send('You have toggled your readiness to age-up to {0}. Waiting for all players in world to ready-up before aging.'.format(toggle))

                # Close
                cursor.close()
                cnx.close()
            else:
                await message.channel.send("Profile Doesn't exisit to age. See `!help`")

    # When the message isn't in a "simulator" channel.
    elif(message.content.startswith('!') and not (message.channel.name == 'Simulator' or message.channel.name == 'simulator')):
        logger.info('{0}, {1} used a command in the wrong channel in {2}'.format(message.author.id, message.author, message.guild.name))
        await message.channel.send('Command in wrong channel. Use the Simulator channel in order to avoid spam. Thanks!')

# initialize the loop
client.run('{0}'.format(open('keys/token.txt', 'r').read()))
