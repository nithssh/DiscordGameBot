import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run('Njg2MTk3OTM2NTM4Nzc5NjQ4.XmTtxg.fDdV0r1FJDNDn5UTqTBW4PJdmYc')