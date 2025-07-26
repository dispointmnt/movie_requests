# This example requires the 'message_content' intent.

import discord
from discord.ui import View, Button
from bot_front import *
# from discord import app_commands
from discord.ext import commands
from os import environ
from dotenv import load_dotenv

load_dotenv()
token = environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

command_buffer = {}
"""
{user_id: {cmd:command, value1:value1, value2:value2...}}
"""
def validate_author(message_id, user_id):
    return(user_id in command_buffer.keys() and message_id == command_buffer[user_id]["message_id"])

class RemoveButton(View):
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary)
    async def remove_request(self, interaction: discord.Interaction, button: discord.Button):
        code = remove_from_requests(command_buffer[interaction.user.id]["query_list"][command_buffer[interaction.user.id]["index"]], interaction.user.id)
        if code == 1:
            await interaction.response.send_message(f"Removed \"{command_buffer[interaction.user.id]['query_list'][command_buffer[interaction.user.id]['index']]['primaryTitle']}\" successfully!", ephemeral=True)
        if code == 0:
            await interaction.response.send_message("A problem occurred oops msg me when this happens ill fix it", ephemeral=True)

class RequestNavigator(View):
    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary)
    async def update_ui_backwards(self, interaction: discord.Interaction, button: discord.Button):
        if not validate_author(interaction.message.id, interaction.user.id):
            await interaction.response.defer()
            return
        command_buffer[interaction.user.id]["index"] -= 1
        if (command_buffer[interaction.user.id]["index"] < 0):
            command_buffer[interaction.user.id]["index"] = command_buffer[interaction.user.id]["total"]
        
        rendering = render(command_buffer[interaction.user.id])
        await interaction.response.edit_message(embed=rendering["embed"], view=self)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.primary)
    async def submit_request(self, interaction: discord.Interaction, button: discord.Button):
        if not validate_author(interaction.message.id, interaction.user.id):
            await interaction.response.defer()
            return
        code = add_to_requests(command_buffer[interaction.user.id]["query_list"][command_buffer[interaction.user.id]["index"]], interaction.user.id)
        
        if code == 2:
            await interaction.response.send_message(f"You've already requested this movie. Would you like to unrequest it?", ephemeral=True, view=RemoveButton())
        if code == 1:
            await interaction.response.send_message(f"Requested \"{command_buffer[interaction.user.id]['query_list'][command_buffer[interaction.user.id]['index']]['primaryTitle']}\" successfully.")
        if code == 0:
            await interaction.response.send_message("A problem occurred oops msg me when this happens ill fix it", ephemeral=True)
        
    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary)
    async def update_ui_forward(self, interaction: discord.Interaction, button: discord.Button):
        if not validate_author(interaction.message.id, interaction.user.id):
            await interaction.response.defer()
            return
        command_buffer[interaction.user.id]["index"] += 1
        if (command_buffer[interaction.user.id]["index"] > command_buffer[interaction.user.id]["total"]):
            command_buffer[interaction.user.id]["index"] = 0

        rendering = render(command_buffer[interaction.user.id])
        await interaction.response.edit_message(embed=rendering["embed"], view=self)
        
class QueueNavigator(View):

    def __init__(self, page=1, max_page=1, timeout = 180):
        super().__init__(timeout=timeout)
        self.page = page
        self.max_page = max_page

    @discord.ui.button(label="<<", style=discord.ButtonStyle.primary)
    async def queue_backward(self, interaction: discord.Interaction, button: discord.Button):
        if not validate_author(interaction.message.id, interaction.user.id):
            await interaction.response.defer()
            return
        
        command_buffer[interaction.user.id]["page"] -= 1
        if (command_buffer[interaction.user.id]["page"] < 0):
            command_buffer[interaction.user.id]["page"] = len(command_buffer[interaction.user.id]["queue"])//command_buffer[interaction.user.id]["entries_pp"]
        
        rendering = render(command_buffer[interaction.user.id])
        await interaction.response.edit_message(embeds=rendering["embeds"], view=self)
    # @discord.ui.button(label=f"{}/{}", style=discord.ButtonStyle.gray)
    # async def do_nothing(self, interaction: discord.Interaction, button: discord.Button):
    #     pass
    @discord.ui.button(label=">>", style=discord.ButtonStyle.primary)
    async def queue_forward(self, interaction: discord.Interaction, button: discord.Button):
        if not validate_author(interaction.message.id, interaction.user.id):
            await interaction.response.defer()
            return
        
        command_buffer[interaction.user.id]["page"] += 1
        if (command_buffer[interaction.user.id]["page"] > len(command_buffer[interaction.user.id]["queue"])//command_buffer[interaction.user.id]["entries_pp"]):
            command_buffer[interaction.user.id]["page"] = 0
        
        rendering = render(command_buffer[interaction.user.id])
        await interaction.response.edit_message(embeds=rendering["embeds"], view=self)
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    # await bot.tree.sync(guild=discord.Object(id = 499186928332046336))
    await bot.tree.sync()
    print(f'Synced slash commands (hopefully)') 

"""
queue:

Sees the current queue.
"""
@bot.hybrid_command(name='queue', with_app_command=True, description="Views the current requests")
async def queue(ctx):
    print(f"{ctx.author.name}: queue")
    command_buffer[ctx.author.id] = get_queue()
    rendering = render(command_buffer[ctx.author.id])
    
    msg = await ctx.send(embeds=rendering["embeds"], view=QueueNavigator(), ephemeral=True)
    command_buffer[ctx.author.id]["message_id"] = msg.id

"""
request:

Adds to the queue
"""
@bot.hybrid_command(name='request', with_app_command=True, description="Request a movie to watch")
async def display_request_ui(ctx, args):
    print(f"{ctx.author.name}: request")
    command_buffer[ctx.author.id] = get_query(args)
    rendering = render(command_buffer[ctx.author.id])
    
    msg = await ctx.send(embed=rendering["embed"], view=RequestNavigator(), ephemeral=True)
    command_buffer[ctx.author.id]["message_id"] = msg.id

"""
archive:

views the archive of watched movies
"""
@bot.hybrid_command(name='archive', with_app_command=True, description="List of all movies watched so far")
async def archive(ctx):
    print(f"{ctx.author.name}: archive")
    await ctx.send("ill make it later")

"""
watch:

Puts a movie into archive and out of requests
"""
@bot.hybrid_command(name='watch', with_app_command=True, description="Sets a movie as watched into the archive")
async def watch(ctx, arg):
    print(f"{ctx.author.name}: watch")
    await ctx.send("watch movie")

"""
rate:

Puts a movie into archive and out of requests
"""
@bot.hybrid_command(name='rate', with_app_command=True, description="Rate a watched movie out of 10")
async def watch(ctx, arg):
    await ctx.send("watch movie")

bot.run(token)