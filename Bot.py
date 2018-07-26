import discord
from discord.ext.commands import Bot
from discord.ext import commands
from functions import edit_json,read_json
import asyncio
import time 
import os


Client = discord.Client()
client = commands.Bot(command_prefix = "!")

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

    


bot=commands.Bot(command_prefix='!')

reaction_roles=read_json('reaction_roles')
active_messages=[]

approved_roles=['Admin']

#Checks if members role is in approved roles
def is_approved():
	def predicate(ctx):
		if ctx.message.author is ctx.message.server.owner:
			return True
		return 	any(role.name in approved_roles for role in ctx.message.author.roles)
	return commands.check(predicate)

@bot.event
async def on_ready():
	print(bot.user.name)
	print(bot.user.id)
	for server in bot.servers:
		print(server.name)

@is_approved()
@bot.command(pass_context=True)
async def add_er(ctx,emoji:str=None,role:discord.Role=None):
	'''Add an Emoji that assigns a Role'''
	if (emoji or role) is None:
		await bot.say('Missing arguments `Emoji` or `@Role`')
		return
	bot_member=discord.utils.get(ctx.message.server.members,id=bot.user.id)
	if role.position >= bot_member.top_role.position:
		await bot.say("Can't assign that role, bot role needs to be raised.")
		return
	reaction_roles[emoji]=role.id
	edit_json('reaction_roles',reaction_roles)
	await bot.say('{} will assign members to {}'.format(emoji,role.mention))

@is_approved()
@bot.command(pass_context=True)
async def remove_er(ctx,emoji):
	'''Remove an Emoji that assigns a Role'''
	role=discord.utils.get(ctx.message.server.roles,id=reaction_roles[emoji])
	await bot.say('{} will no longer assign {}'.format(emoji,role.mention))
	del reaction_roles[emoji]
	edit_json('reaction_roles',reaction_roles)

@bot.command(pass_context=True)
async def er(ctx):
	'''React with Emojis to assign a role to yourself'''
	if len(reaction_roles)==0:
		await bot.say("No emojis have been assigned to roles")
		return
	global active_messages
	server=ctx.message.server
	message=''
	for emoji,role in reaction_roles.items():
		role=discord.utils.get(server.roles,id=role)
		message+='{} will assign {}\n'.format(emoji,role.mention)
	msg = await bot.say(message)
	for emoji in reaction_roles.keys():
		await bot.add_reaction(msg,emoji)
	active_messages.append(msg.id)

@bot.event
async def on_reaction_add(reaction,user):
	if reaction.message.id in active_messages and reaction.emoji in reaction_roles and user != bot.user:
		role=discord.utils.get(reaction.message.server.roles,id=reaction_roles[reaction.emoji])
		for r_id in reaction_roles.values():
			e_role=discord.utils.get(reaction.message.server.roles,id=r_id)
			if e_role in user.roles:
				await bot.remove_roles(user,e_role)
		await bot.remove_reaction(reaction.message,reaction.emoji,user)
		await bot.add_roles(user,role)






client.run(os.getenv('TOKEN'))
