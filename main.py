import re
import discord
import random
import requests
from discord.ui import Button, View
from bs4 import BeautifulSoup
from discord import Intents
from random import shuffle
import server_info
from discord.ext import commands
from keep_alive import keep_alive

intents = Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

user_data = {}


class UserInstance:
    def __init__(self, name, time_spent):
        self.name = name
        self.time_spent = time_spent


# initialization
@client.event
async def on_ready():
    print('Successfully logged in as {0.user}'.format(client))
    channel = client.get_channel(424665181159686156)
    members = channel.members
    msg = ""

    for member in members:
        msg += member.name + ", "
        new_user = UserInstance(member.name, 0)
        user_data[new_user.name] = new_user.time_spent

    return user_data
    #await ctx.channel.send(msg)


users = user_data
print(users)


@client.command()
async def here(ctx):
    channel = client.get_channel(424665181159686156)
    members = channel.members
    msg = ""

    for member in members:
        msg += member.name + ", "
        new_user = UserInstance(member.name, 0)
        user_data[new_user.name] = new_user.time_spent

    print(user_data)
    #await ctx.channel.send(msg)


# Display all valid commands in chat
@client.command()
async def commands(ctx):
    commands_string = "```Commands:\n.commands - Display this message.\n.purge [n] - Delete the last n messages from chat\n.define [word] - Display the definition of a word.\n.scramble - Scramble the words of the most recent message in chat.\n.roll [n] - Simulate the rolling of an n-sided die.```"
    await ctx.channel.send(commands_string)


@client.command()
async def test(ctx, amount=1):
    if (amount > 0):
        buttonYes = Button(label="Ye", style=discord.ButtonStyle.green)

        buttonNo = Button(label="Nah", style=discord.ButtonStyle.danger)

        async def button_callbackNo(interaction2):
            #await interaction2.response.send_message("Not deleting.")
            buttonNo.disabled = True
            buttonYes.disabled = True
            #buttonNo.label = "-"  # change the button's label to something else
            await interaction2.response.edit_message(
                view=view)  # edit the message's view
            #await msg.delete()

        async def button_callbackYes(interaction1):
            #await interaction1.response.send_message("Deleting.")
            buttonYes.disabled = True
            buttonNo.disabled = True
            #buttonYes.label = "-"  # change the button's label to something else
            await interaction1.response.edit_message(
                view=view)  # edit the message's view

        buttonYes.callback = button_callbackYes
        buttonNo.callback = button_callbackNo

        view = View()
        view.add_item(buttonYes)
        view.add_item(buttonNo)
        msg = await ctx.send(
            f"Do you really want to delete {amount} messages?", view=view)


# clear 'amount' number of chat messages (default = 1 including prune command message)
@client.command()
async def purge(ctx, amount=1):
    if (amount > 0):
        buttonYes = Button(label="Ye", style=discord.ButtonStyle.green)

        buttonNo = Button(label="Nah", style=discord.ButtonStyle.danger)

        async def button_callbackNo(interaction2):
            buttonNo.disabled = True
            buttonYes.disabled = True
            await msg.delete()
            await ctx.channel.purge(limit = 1)

        async def button_callbackYes(interaction1):
            buttonYes.disabled = True
            buttonNo.disabled = True
            await ctx.channel.purge(limit=amount + 2)
            #await msg.delete()

        buttonYes.callback = button_callbackYes
        buttonNo.callback = button_callbackNo

        view = View()
        view.add_item(buttonYes)
        view.add_item(buttonNo)
        msg = await ctx.send(
            f"Do you really want to delete {amount} messages?", view=view)


@client.command()
async def define(ctx, word):

    url = 'https://www.merriam-webster.com/dictionary/' + str(word)
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    definition = soup.find(class_="dtText")

    if (definition == None):
        to_send = "```I can't find that word in the dictionary.```"
        await ctx.channel.send(to_send)
    else:
        to_send = "```" + definition.text + "```"
        print(to_send)
        await ctx.channel.send(to_send)


# generate random number between 0 and amount
@client.command()
async def roll(ctx, amount=2.0):
    amount = round(amount)
    if (amount > 1 and type(amount) == int):
        amt = random.randrange(amount) + 1
        await ctx.channel.send("You rolled: " + str(amt))
    else:
        await ctx.channel.send("Enter a number greater than 1.")


# scramble the words of the latest message in chat
@client.command()
async def scramble(ctx):

    message = (await ctx.channel.history(limit=2).flatten())[-1]

    lst = list((message.content).split(" "))
    shuffle(lst)
    scrambled = ' '.join(lst)
    await message.channel.send(scrambled)


# redirect hyperlinks to links text channel
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    val = re.findall('^(val)$|valorant|valarante', message.content.lower())
    if (val):
        await message.channel.send("<@" + str(message.author.id) + ">" +
                                   " That game is bad. Sorry.")

    # urls for links
    urls = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        message.content.lower())
    # urls for discord gifs, to be excluded from link filtering
    gifs = re.findall('https://tenor.com*', message.content.lower())

    # filter for all links excluding discord gifs
    if (not gifs):
        if urls and message.channel.id == server_info.channel_src:
            await message.delete()

            # change bot message destination to links chat
            message.channel.id = server_info.channel_dest

            # ping user who sent link
            await message.channel.send("<@" + str(message.author.id) + ">" +
                                       str(message.content))

        # allow for bot commands
        await client.process_commands(message)

        message.channel.id = server_info.channel_src


# ping server to keep bot from logging off
keep_alive()

client.run(server_info.TOKEN)
