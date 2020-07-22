"""This file should contain all the functions that are used by the various file across the project\n Contains: b_exists, parse_message"""
import json
import re

import mysql.connector

# Database connection's config. Reads from a json file, converts to dict from obj.
# Reading config from json file instead of defining config(dict) in this code file.
with open('secrets/DB_login.json', 'r') as f:
    config = json.load(f)


def user_profile_exisits(authorID):
    """
    This fuction check if a user profile exists.\n
    Should be used before proceeding with a command as standard practise.\n
    Returns:\n
    >`True` if user profile exists in gamedata.maintable\n
    >`False` if profile doesn't exist in the same."""

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

    cursor.close()
    cnx.close()

    return result


def parse_message(message, command_str):
    """Parses the message into list of all the words in message that are seperated by whitespace\n 
    Parameters:
            message -- pass the message as-is
            command_str -- the command string that should be removed from the parsed message"""

    # Substitute the command_str with nothing (remove the command_str)
    message_without_command = re.sub(command_str, '', message.content)
    # Split the message into a list of all the words that are seperated by whitespaces.
    output = message_without_command.split(' ')
    # remove the first element in the list, As after subsitution the string will start with a whitespace, which on split will create a empty first element.
    output.pop(0)
    return output
