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
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Database connection's config. Reads from a json file, converts to dict from obj.
# Reading config from json file instead of defining config(dict) in this code file.
with open('secrets/DB_login.json', 'r') as f:
    config = json.load(f)

# Database connection and cursors
cnx = mysql.connector.connect(**config)
cursor_buffered = cnx.cursor(buffered=True)
cursor_unbuffered = cnx.cursor(buffered=False)

# Events
@client.event
async def on_ready():
    print('Successfully logged in as {0}'.format(client.user))
    logger.info('Successfully logged in as {0}'.format(client.user))

# Commands
@client.event
async def on_message(message):

    # Respond only to messages in channels named "simulator" to avoid server wide spam.
    if ((message.channel.name == 'simulator' and message.content.startswith('!')) or
            (message.channel == "DMChannel" and message.content.startswith('!'))):

        # Don't process messages from the bot. [anti-recursion]
        if message.author == client.user:
            return
        else:
            # Variables used by all functions
            user_id = {'discord_Uid': message.author.id}

        # !help - send the help message from file.
        if message.content.startswith('!help'):
            logger.info('{0}, {1} invoked !help command.'.format(
                message.author.id, message.author))
            with open('message_templates/help_message.txt', 'r') as f:
                await message.channel.send(f.read())

        # !create - create a new world.
        if message.content.startswith('!create'):
            logger.info('{0}, {1} invoked !create command'.format(
                message.author.id, message.author))

            # If user doesn't have exisiting profile
            if (utilities.user_profile_exisits(message.author.id) == False):

                await message.channel.send("Profile doesn't exist.")

                query_add_profile = (
                    "INSERT INTO gamedata.maintable "

                    "(discord_userID, discord_username, World_ID, Name, Gender, Age, "
                    "Occupation, Location, Happiness, Health, Smarts, Looks, Schedule_deletion, Bank) "

                    "VALUES (%(did)s, %(dun)s, %(wor)s, %(n)s, %(g)s, %(a)s, "
                    "%(o)s, %(l)s, %(hap)s, %(hea)s, %(sma)s, %(loo)s, %(del)s, %(bnk)s )")

                # Generate World_ID. Retrive the last value of world_id and increment
                query_max_world_id = (
                    "SELECT World_ID FROM gamedata.maintable ORDER BY World_ID DESC LIMIT 1")
                cursor_unbuffered.execute(query_max_world_id)
                max_world_id = cursor_unbuffered.fetchall()
                if (len(max_world_id) != 0):
                    generated_world_id = 1
                    generated_world_id += max(max_world_id[0])
                else:
                    generated_world_id = 1

                # Parse the message into its sub components to use in world creation
                message_parts = utilities.parse_message(message, '!create')

                for part in message_parts:
                    try:
                        username = part.split('#')
                        retrived_user_id = discord.utils.get(
                            client.get_all_members(), name=username[0], discriminator=username[1]).id
                        gender = random.choice(['male', 'female'])

                        data_profile = {
                            'did': retrived_user_id,
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

                        cursor_unbuffered.execute(
                            query_add_profile, data_profile)
                        # Save to DB
                        cnx.commit()
                        await message.channel.send('Profile successfully created. use `!profile` to see details.')
                        logger.info("{0}, {1} profile creation successful.".format(
                            user_id, username[0]))

                    except:
                        cnx.rollback()
                        await message.channel.send('Profile creation failed. '
                                                   'This is most probably due to incorrect command arguments. '
                                                   'See `!help` to find correct usage.')
                        logger.error("{0}, {1} profile creation failed".format(
                            message.author.id, message.author))

            else:
                # Profile already exists
                await message.channel.send("""Profile already exists. Players can have only one profile at a time. 
                Use `!profile` command to see summary. 
                Use !surrender command to delete profile to create new one in a new world.""")
                logger.info("{0}, {1} profile already exists.".format(
                    message.author.id, message.author))

        # !profile - send profile summary.
        if message.content.startswith('!profile'):
            logger.info('{0}, {1} invoked !profile command'.format(
                message.author.id, message.author))

            if (utilities.user_profile_exisits(message.author.id)):

                # Retrive the record from the DB
                query_record = ("SELECT * FROM gamedata.maintable "
                                "WHERE discord_userID=%(discord_Uid)s")
                cursor_unbuffered.execute(query_record, user_id)
                record = cursor_unbuffered.fetchall()

                # Ready the data for next operations.
                for row in record:
                    logger.info('row from record loaded.')

                # Load the message from the file
                with open('message_templates/profile_summary.txt', 'r') as f:
                    profile_message = f.read().format(
                        row[3],
                        row[5],
                        row[4],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
                        row[11],
                        row[13],
                        row[2],
                        row[1])

                await message.channel.send(profile_message)

            else:
                await message.channel.send("""@{0}'s profile doesn't exist. 
                Invoke `!help` to get started.""".format(message.author))
                logger.info("{0}, {1} profile doesn't exist doesn't to summarize.".format(
                    message.author.id, message.author))

        # !surrender - delete current profile.
        if message.content.startswith('!surrender'):
            # profile deletion
            logger.info('{0}, {1} Invoked !surrender command'.format(
                message.author.id, message.author))

            if(utilities.user_profile_exisits(message.author.id)):

                # UPDATE the schedule_deletion field to 1 (true).
                query_update_deletion_on = ("UPDATE gamedata.maintable "
                                            "SET Schedule_deletion = '1' "
                                            "WHERE discord_userID=%(discord_Uid)s")
                cursor_buffered.execute(query_update_deletion_on, user_id)
                cnx.commit()

                # The Function that gets called after 2 mins.
                def deletion_function():
                    # the b_exists validation is required to prevent exceptions due to multiple
                    # threads deleting the same thread, due to multiple commands from same user.
                    if (utilities.user_profile_exisits(message.author.id)):
                        # Retrive updated record
                        query_schedule_deletion = (
                            "SELECT Schedule_deletion FROM gamedata.maintable "
                            "WHERE discord_userID=%(discord_Uid)s")

                        cursor_buffered.execute(
                            query_schedule_deletion, user_id)

                        for Schedule_deletion in cursor_buffered:
                            b_deletion = Schedule_deletion

                        if (b_deletion[0] == 1):
                            # Procede with deletion.
                            query_delete_profile = ("DELETE FROM gamedata.maintable "
                                                    "WHERE discord_userID=%(discord_Uid)s")
                            try:
                                cursor_buffered.execute(
                                    query_delete_profile, user_id)
                                cnx.commit()
                                logger.info('{0}, {1} profile was successfully deleted.'.format(
                                    message.author.id, message.author))
                                # TODO send success message

                            except:
                                cnx.rollback()
                                logger.error("{0}, {1}'s profile was not deleted due to an error.".format(
                                    message.author.id, message.author))
                                # TODO send operation failure message
                        else:
                            # The deletion has been cancelled
                            logger.info('The deletion of {0}, {1} profile has been cancelled'.format(
                                message.author, message.author.id))
                    else:
                        logger.info('the profile of {0}, {1} has already been deleted'.format(
                            message.author, message.author.id))

                # start the timer
                timer = threading.Timer(120.0, deletion_function)
                await message.channel.send('The profile will be deleted after 2 mins,\n'
                                           'Use the `!cancel_surrender` command to ABORT the deletion.')
                timer.start()
                logger.info('Deletion timer started for {0}, {1}'.format(
                    message.author, message.author.id))

            else:
                await message.channel.send("""@{0} 's profile doesn't exist to delete. 
                Invoke `!help` to see help.""".format(message.author))
                logger.info(
                    "{0}, {1} profile doesn't exist to delete. [from:!surrender]").format(
                        message.author.id, message.author)

        # !cancel_surrender - cancel the profile deletion queuing.
        if (message.content.startswith('!cancel_surrender')):
            logger.info('The !cancel_deletion command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))

            if (utilities.user_profile_exisits(message.author.id)):

                # UPDATE the schedule_deletion field to 0 (False).
                query_update_deletion_off = ("UPDATE gamedata.maintable "
                                             "SET Schedule_deletion = '0' "
                                             "WHERE discord_userID=%(discord_Uid)s")
                try:
                    cursor_buffered.execute(query_update_deletion_off, user_id)
                    cnx.commit()
                    logger.info('The !cancel_surrender command has been successfully executed for '
                                '{0}, {1}'.format(message.author, message.author.id))

                    await message.channel.send('The profile deletion (surrender) has been successfully ABORTED.\n'
                                               'You can continue playing without any change.')
                except:
                    logger.error('There was an error in executing the !cancel_surrender command for {0}, {1}'.format(
                        message.author, message.author.id))
                    await message.channel.send("There was an error in cancelling the deletion.")

            else:
                await message.channel.send("""@{0} 's profile doesn't exist. 
                Invoke `!help` to see help.""".format(message.author))
                logger.info(
                    "{0}, {1} profile doesn't exist. [from:!cancel_surrender]".format(
                        message.author.id, message.author))

        # !age - increase the age of everyone in the world. [progress the game]
        # toggles ready_to_age of the user, and triggers aging if everyone in world is ready.
        if (message.content.startswith('!age')):
            logger.info('The !age command has been invoked by {0}, {1}'.format(
                message.author, message.author.id))

            if(utilities.user_profile_exisits(message.author.id)):

                # get current value of ready_to_age of user
                query_get_aging_status = ("SELECT ready_to_age FROM gamedata.maintable "
                                    "WHERE discord_userID = %(discord_Uid)s")
                cursor_unbuffered.execute(query_get_aging_status, user_id)
                current_aging_status = cursor_unbuffered.fetchall()

                set_aging_status = ("UPDATE gamedata.maintable "
                                    "SET ready_to_age = %(aging_status)s "
                                    "WHERE discord_userID = %(discord_Uid)s")

                # Toggle the ready_to_age field of user
                if (current_aging_status[0] == 1):
                    new_aging_status_data = {
                        'aging_status': 0,
                        'discord_Uid': message.author.id
                    }
                    cursor_unbuffered.execute(
                        set_aging_status, new_aging_status_data)
                    cnx.commit()
                else:
                    new_aging_status_data = {
                        'aging_status': 1,
                        'discord_Uid': message.author.id
                    }
                    cursor_unbuffered.execute(
                        set_aging_status, new_aging_status_data)
                    cnx.commit()

                # Check if all profiles in world are ready

                # Get the world_id of the world to be aged up
                query_get_world_id = ("SELECT World_ID FROM gamedata.maintable "
                                "WHERE discord_userID = %(discord_Uid)s")
                cursor_unbuffered.execute(query_get_world_id, user_id)
                world_id = cursor_unbuffered.fetchall()

                # load the current ready_to_age of all the users in the world
                query_get_ready_status = ("SELECT ready_to_age FROM gamedata.maintable "
                                          "WHERE World_ID = %s")
                cursor_unbuffered.execute(query_get_ready_status, world_id[0])
                current_ready_status_data = cursor_unbuffered.fetchall()

                sum_ready_to_age = 0
                for status in current_ready_status_data:
                    sum_ready_to_age += status[0]

                # if all true
                if (sum_ready_to_age/len(current_ready_status_data) == 1):
                    ager = Aging()
                    ager.age_up(message)
                    await message.channel.send('A year has passed in the World. Everyone is a year older.')
                else:
                    # For pretty printing the message for user.
                    # Changes aging_status to True or False (which is user-readable format)
                    if(new_aging_status_data['aging_status'] == 1):
                        toggle = True
                    else:
                        toggle = False
                    await message.channel.send("""You have toggled your readiness to age-up to {0}. 
                    Waiting for all players in world to ready-up before aging.""".format(toggle))

            else:
                await message.channel.send("Profile Doesn't exisit to age. See `!help`")

    # When the message isn't in a "simulator" channel.
    elif(message.content.startswith('!') and not
         (message.channel.name == 'Simulator' or message.channel.name == 'simulator')):

        logger.info('{0}, {1} used a command in the wrong channel in {2}'.format(
            message.author.id, message.author, message.guild.name))
        await message.channel.send('Command in wrong channel. '
                                   'Use the Simulator channel in order to avoid spam. Thanks!')

# initialize the loop
client.run('{0}'.format(open('keys/token.txt', 'r').read()))
