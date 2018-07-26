import discord
from discord.ext import commands
import asyncio
import time 

#---------------------- JSON Stuff -------------------------
import os,json
def read_json(file_name):
	if file_name.endswith('.json')==False:
		file_name=file_name+'.json'
	if not os.path.isfile(file_name):
		list_name=open(file_name,"w+")
		list_name={}
	else:
		try:
			with open(file_name) as f:
				list_name = json.load(f)
		except ValueError:
			list_name={}
	return list_name

def edit_json(file_name,items):
	if file_name.endswith('.json')==False:
		file_name=file_name+'.json'
	with open(file_name,"w") as f:
		json.dump(items,f)
#----------------------------General---------------------------

client = commands.Bot(command_prefix = "!")

reaction_roles=read_json('reaction_roles')
active_messages=[]
approved_roles=['Admin']


@client.event
async def on_ready():
    print("JAY, YOURE BOT IS READY!")
    print(client.user.name)
    print(client.user.id)
    for server in client.servers:
        print(server.name)
#----------------------Member join/leave---------------------
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

@client.event
async def on_member_join(member):
        role = discord.utils.get(member.server.roles, name='members')
        await client.add_roles(member,role)

#---------------------Music Player Code---------------------


@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)


@client.command(pass_context=True)
async def leave(ctx):
        server = ctx.message.server
        voice_client = client.voice_client_in(server)
        await voice_client.disconnect()
 


#-------------------------Reaction Roles----------------------
def is_approved():
	def predicate(ctx):
		if ctx.message.author is ctx.message.server.owner:
			return True
		return 	any(role.name in approved_roles for role in ctx.message.author.roles)
	return commands.check(predicate)


@is_approved()
@client.command(pass_context=True)
async def add_er(ctx,emoji:str=None,role:discord.Role=None):
	'''Add an Emoji that assigns a Role'''
	if (emoji or role) is None:
		await client.say('Missing arguments `Emoji` or `@Role`')
		return
	client_member=discord.utils.get(ctx.message.server.members,id=client.user.id)
	if role.position >= client_member.top_role.position:
		await client.say("Can't assign that role, client role needs to be raised.")
		return
	reaction_roles[emoji]=role.id
	edit_json('reaction_roles',reaction_roles)
	await client.say('{} will assign members to {}'.format(emoji,role.mention))

@is_approved()
@client.command(pass_context=True)
async def remove_er(ctx,emoji):
	'''Remove an Emoji that assigns a Role'''
	role=discord.utils.get(ctx.message.server.roles,id=reaction_roles[emoji])
	await client.say('{} will no longer assign {}'.format(emoji,role.mention))
	del reaction_roles[emoji]
	edit_json('reaction_roles',reaction_roles)

@client.command(pass_context=True)
async def er(ctx):
	'''React with Emojis to assign a role to yourself'''
	if len(reaction_roles)==0:
		await client.say("No emojis have been assigned to roles")
		return
	global active_messages
	server=ctx.message.server
	message=''
	for emoji,role in reaction_roles.items():
		role=discord.utils.get(server.roles,id=role)
		message+='{} will assign {}\n'.format(emoji,role.mention)
	msg = await client.say(message)
	for emoji in reaction_roles.keys():
		await client.add_reaction(msg,emoji)
	active_messages.append(msg.id)

@client.event
async def on_reaction_add(reaction,user):
	if reaction.message.id in active_messages and reaction.emoji in reaction_roles and user != client.user:
		role=discord.utils.get(reaction.message.server.roles,id=reaction_roles[reaction.emoji])
		await client.remove_reaction(reaction.message,reaction.emoji,user)
		await client.add_roles(user,role)

#------------------------------------Token-----------------------------------


client.run(os.getenv('TOKEN'))
