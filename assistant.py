# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# https://discordpy.readthedocs.io/en/latest/api.html?highlight=client#discord.Intents
client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    if discord.utils.get(message.mentions, id=client.user.id) == None:
        print("Not mention me, sad :(")
        return

    if 'hi' in message.content:
        response = "hi master"
        await message.channel.send(response)
    else:
        print(message)

    if str(message.attachments) == "[]": # Checks if there is an attachment on the message
        return
    else: # If there is it gets the filename from message.attachments
        split_v1 = str(message.attachments).split("filename='")[1]
        filename = str(split_v1).split("' ")[0]
        print(filename)
        if filename.endswith(".csv"): # Checks if it is a .csv file
            await message.attachments[0].save(fp="CsvFiles/{}".format(filename)) # saves the file



client.run(TOKEN)