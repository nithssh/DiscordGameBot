import json
import logging

import mysql.connector

# Database connection's config. Reads from a json file, converts to dict from obj.
# Reading config from json file instead of defining config(dict) in this code file.
with open('keys/DB_login.json', 'r') as f:
    config = json.load(f)

# File logger
Agelogger = logging.Logger('AgeLogger')
Agelogger.setLevel(logging.INFO)
# Current mode is a = append. r for read, w for write, r+ for both and w+ for both with resetting.
handler = logging.FileHandler(
    filename='AgeLog.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
Agelogger.addHandler(handler)


class Aging:

    # +age
    def age_up(self, message):
        """ Increments the age of everyone in the world, Affects the corestats of the profiles based on age, and  tiggers random world events"""
        Agelogger.info('{0}, {1} has invoked !age command'.format(message.author.id, message.author))
            
        # Connect to the database
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor(buffered=False)
        userid = {'discord_Uid': message.author.id}

        # Get the world_id of the world to be aged up
        get_world_id = ("SELECT World_ID FROM gamedata.maintable "
                        "WHERE discord_userID = %(discord_Uid)s")
        cursor.execute(get_world_id, userid)
        world_id = cursor.fetchall()

        # load the current age of all the users in the world and increment
        get_age = ("SELECT discord_userID, Age FROM gamedata.maintable "
                    "WHERE World_ID = %s")
        cursor.execute(get_age, world_id[0])
        current_age_data = cursor.fetchall()
        for discord_userID, Age in current_age_data:
            new_age = Age + 1

            new_age_data = {
                'age': new_age,
                'discord_Uid': discord_userID
            }
            update_age = ("UPDATE gamedata.maintable "
                        "SET Age = %(age)s "
                        "WHERE discord_userID=%(discord_Uid)s")
            cursor.execute(update_age, new_age_data)
            Agelogger.info('{0}, {1} has aged'.format(message.author.id, message.author))
        
        cnx.commit()

        #close
        cursor.close()
        cnx.close()

        Agelogger.info('the world with {0}, {1} has aged.'.format(message.author, message.author.id))
        