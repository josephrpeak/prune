import discord
import re
import time
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
async def prune(ctx, amount=1):
  await ctx.channel.purge(limit=amount+1)

# redirect hyperlinks to links text channel
@client.event
async def on_message(message):
  if message.author == client.user:
      return

  # urls for links
  urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',message.content.lower())
  # urls for discord gifs, to be excluded from link filtering
  gifs = re.findall('https://tenor.com*', message.content.lower())

  # filter for all links excluding discord gifs
  if(not gifs):
    if urls and message.channel.id == server_info.channel_src:
      msg = await message.channel.send("<@" + str(message.author.id) + ">" + " I moved your stupid link to the links chat, idiot. (Deleting in 10s)")
      await message.delete()

      # delete bot's message after 10s
      time.sleep(10)
      await msg.delete()

      # change bot message destination to links chat
      message.channel.id = server_info.channel_dest

      # ping user who sent link
      await message.channel.send("<@" + str(message.author.id) + ">" + str(message.content))

    # allow for bot commands
    await client.process_commands(message)
  
    message.channel.id = server_info.channel_src
    
# ping server to keep bot from logging off
keep_alive()
client.run(server_info.TOKEN)
