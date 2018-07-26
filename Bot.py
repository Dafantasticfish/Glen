import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time 
import os


players = {}

Client = discord.Client()
client = commands.Bot(command_prefix = "!")
print(discord.__version__)

@client.event
async def on_ready():
    print("JAY, YOURE BOT IS READY!")

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.server.channels, name = 'welcome')
    emb = (discord.Embed(title = " Welcome to " +str(member.server), color = 484848))
    emb.set_author(name = member.display_name+" joined", icon_url = member.avatar_url)
    
    await client.send_message(channel, embed=emb)

    
@client.event
async def on_member_remove(member):
    channel = discord.utils.get(member.server.channels, name = 'goodbye')
    emb = (discord.Embed(title = " Goodbye :frowning2:  ", color = 484848))
    emb.set_author(name = member.display_name+" Left", icon_url = member.avatar_url)
    
    await client.send_message(channel, embed=emb)    

@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()







client.run(os.getenv('TOKEN'))
