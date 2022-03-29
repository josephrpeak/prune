import discord
import re
from server_info import *
from replit import db
from keep_alive import keep_alive

client = discord.Client()

@client.event
async def on_ready():
    print('We have successfully loggged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    message.channel.id = server_info.channel_src

    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message.content.lower())

    if urls and message.channel.id == server_info.channel_dest:
    	await message.channel.send("I moved your stupid link to the links chat, idiot.")
    	await message.delete()
    	message.channel.id = server_info.channel_src
    	await message.channel.send(message.content)

keep_alive()
client.run(server_info.TOKEN)