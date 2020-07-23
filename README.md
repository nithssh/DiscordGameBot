# DiscordLife
A text-based life simulator on Discord (bot). Users can play the game by issuing command to the bot through messages. 

# Installation
## Inviting the bot
Follow this [link]( https://discordapp.com/api/oauth2/authorize?client_id=686197936538779648&permissions=207872&scope=bot) to add the bot to your server.
You require Admin permissions in the server you wish to add the bot to.

To avoid server-wide spam the bot is coded to process commands that are issued in text channels named `simulator` only, and so the creation of such a channel, before or after inviting the bot, within the server is must for playing. 

The bot requires no additional permissions than a regular member in your server -- to read and write messages, and other basic permissions (shown in the invite screen).

# Usage (playing)
You can start playing the game by inviting the bot to your server using the above link and then invoking the `!help` command to get a quick help guide.
`!create` - use this command to create a world with characters in it for the simulation. Only one character is allowed per user across all servers currently.

# Contributing
We welcome contributions from the public! If you'd like to help improve the bot, please fork our project and feel free to tackle any Issues. We also welcome feedback in the form of new issues, so feel free to create new ones for discussion.
The project is currently a monolith.

## Prerequisites
* Python 3.x - The language the bot is primarily written in. https://www.python.org/downloads/
* MySQL - The database server the bot uses to store all the game data. https://www.mysql.com/downloads/

*Dependencies*
* Discord.py - A popular API wrapper for the discord.js written in Python. https://github.com/Rapptz/discord.py
* faker - random data generator. Currently being used in project for address generation. https://github.com/joke2k/faker
* names - random name generator. https://github.com/treyhunner/names
* mysql-connector-python - The connector used to interface with the MySQL database from within python code. Used to query/read/write data to and from the database.

## Configuration

* Install all the prerequisites.

* Install all the dependencies by running the command `pip install -r requirements.txt`.

* Clone the repo.

* Open MySQL workbench and create a schema name `gamedata`, and create a table named `maintable` using
``` SQL
    CREATE TABLE `maintable` (
  `discord_id` varchar(64) NOT NULL,
  `username` varchar(45) DEFAULT NULL,
  `world_id` int DEFAULT NULL,
  `gender` varchar(6) DEFAULT NULL,
  `character_name` varchar(45) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `occupation` varchar(15) DEFAULT NULL,
  `bank` int DEFAULT NULL,
  `address` varchar(60) DEFAULT NULL,
  `happiness` int DEFAULT NULL,
  `health` int DEFAULT NULL,
  `smarts` int DEFAULT NULL,
  `looks` int DEFAULT NULL,
  `deletion` tinyint DEFAULT NULL,
  `aging_ready` tinyint DEFAULT NULL,
  PRIMARY KEY (`discord_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
```
* Within the cloned repo, create a sub directory in the root named `secrets`.

* Create a file named `DB_login.json` and fill it with
``` json
    {
        "user": "*username*",
        "password": "*password*",
        "host": "localhost",
        "database": "gamedata"
    }
```
Replace the above placeholders (*username*, *password*) with your actual MySQL database credentials.

* Create a file in the same sub directory named `botToken.txt` and fill it with the bot’s login token found in it [Discord developer portal](https://discordapp.com/developers/applications) page. You need to create a new application in the dev portal, then head to the BOT section in the left panel and get the bot’s token from there.

## Deployment
You can run the bot by simply running the code like a normal python script. If the bot successfully started you will see a message in the console saying the same with some extra details.

# Credits

# Licence 
 This repo is licensed under the [MIT licence](https://mit-license.org/). See LISENCE file for all the info.