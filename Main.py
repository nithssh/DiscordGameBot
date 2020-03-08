import logging
import discord
import string

client = discord.Client()

#File logger--------------------------------------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Events--------------------------------------------------------

#initialized
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
#prevents recursion
    if message.author == client.user:
        return

#!help 
    if message.content.startswith('!help'):
        with open('helpfile.txt') as f:
            await message.channel.send(f.read())


client.run('Njg2MTk3OTM2NTM4Nzc5NjQ4.XmTtxg.fDdV0r1FJDNDn5UTqTBW4PJdmYc')