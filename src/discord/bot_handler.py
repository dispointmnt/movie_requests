# This example requires the 'message_content' intent.

import discord
from discord import app_commands
from discord.ext import commands
from os import environ
from dotenv import load_dotenv

load_dotenv()
token = environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    await bot.tree.sync(guild=discord.Object(id = 499186928332046336))
    # await bot.tree.sync()
    print(f'Synced slash commands (hopefully)')

"""
queue:

Sees the current queue.
"""
@bot.hybrid_command(name='queue', with_app_command=True, description="Views the current requests")
async def queue(ctx):
    await ctx.send("the current q")

"""
request:

Adds to the queue
"""
@bot.hybrid_command(name='request', with_app_command=True, description="Request a movie to watch")
async def request(ctx, arg):
    await ctx.send(arg)

"""
archive:

views the archive of watched movies
"""
@bot.hybrid_command(name='archive', with_app_command=True, description="List of all movies watched so far")
async def archive(ctx):
    await ctx.send("artkive")

"""
watch:

Puts a movie into archive and out of requests
"""
@bot.hybrid_command(name='watch', with_app_command=True, description="Sets a movie as watched into the archive")
async def watch(ctx, arg):
    await ctx.send("watch movie")

bot.run(token)