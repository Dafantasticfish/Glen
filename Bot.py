import discord
from discord.ext import commands
import asyncio
import time 
import os,json

#--------------------------------- JSON Stuff --------------

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
#welcome/goodbye----------------------------------------------------

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


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.server.channels, name = 'welcome')
    emb = discord.Embed(title = " Welcome to " +str(member.server), color = 484848)
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

#reaction role----------------------------------------------------

#Checks if members role is in approved roles
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

@is_approved()
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

#---------------------------------------------------
@client.event
async def on_message(message):
	print('a user has sent a message.')
	await client.process_commands(message)


@client.command()
async def owain():
	await client.say('owain smells of shit and looks like woody from suit life of zack and cody @everyone ')

@client.command()
async def jewboy():
	await client.set_image(url="data:image/jpeg;base64,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")
	
@client.command()
async def echo(*args):
	output = ''
	for word in args:
		output += word
		output += ' '
	await client.say(output)
	
	

@client.command(pass_context=True)
async def servers(ctx):
    embed = discord.Embed(title="List of servers Glen Is in",
                            colour=discord.Colour(484848))
    server_list = '' 
    for server in client.servers:
            server_list += f'{server.name} \n'

    embed.add_field(name='servers', value=server_list)
    await client.say




#---------------------------------------------------

client.run(os.getenv('TOKEN'))
