# bot.py
import os

import discord
from dotenv import load_dotenv

from llm.assistant import Assistant
from utils import split
import functools
import typing # For typehinting 

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await client.loop.run_in_executor(None, func)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# https://discordpy.readthedocs.io/en/latest/api.html?highlight=client#discord.Intents
client = discord.Client(intents=discord.Intents.all())
assistant = Assistant()
assistant.init()

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
    async with message.channel.typing():
        response: str = await run_blocking(assistant.invoke, text=message.content) # Pass the args and kwargs here

    if len(response) >= 2000:
        response = split(response, 2000, "\n")

    if type(response) is list:
        for chunk in response:
            await message.channel.send(chunk)
    else:
        await message.channel.send(response)
        

client.run(TOKEN)