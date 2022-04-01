import discord
import re
import server_info
from discord.ext import commands
from keep_alive import keep_alive

client = commands.Bot(command_prefix = '.')

# initialization
@client.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(client))

# clear 'amount' number of chat messages (default = 1 including prune command message)
@client.command()
async def prune(ctx, amount=2):
  await ctx.channel.purge(limit=amount+1)

# redirect hyperlinks to links text channel
@client.event
async def on_message(message):
    if message.author == client.user:
        return
      
    message.channel.id = server_info.channel_src
  
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message.content.lower())

    if urls and message.channel.id == server_info.channel_src:
      await message.channel.send("I moved your stupid link to the links chat, idiot.")
      await message.delete()
      message.channel.id = server_info.channel_dest
      
      await message.channel.send("<@" + str(message.author.id) + ">" + str(message.content))
    await client.process_commands(message)

# ping server to keep bot from logging off
keep_alive()
client.run(server_info.TOKEN)
