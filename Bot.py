import discord
from discord.ext import commands
import rocket_snake as rs
from rocket_snake import constants as const
from pyson import Pyson
import random
import asyncio
import time 

#--------------------------------- JSON Stuff --------------
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
#---------------------------Rocket League Stats---------------------------------
async def get_platform(platform):
    if platform.lower() == 'steam':
        return const.STEAM
    elif platform.lower() == 'ps4':
        return const.PS4
    elif platform.lower() == 'xbox':
        return const.XBOX1

async def get_tier(ptier):
    tierlist = await rlsclient.get_tiers()
    tier = tierlist[ptier]

    return tier.name

@bot.command(name = 'stats')
async def get_stats(ctx, uid, platform = const.STEAM):

    if platform != const.STEAM:
        platform = await get_platform(platform)

    player = await rlsclient.get_player(uid, platform)
    avatar = player.avatar_url

    if avatar is None:
        avatar = "http://cdn.edgecast.steamstatic.com/steamcommunity/public/images/avatars/78/" \
                 "781cd87d570a7df1e51994d39dc41b09f1a8cf3a_full.jpg"

    stats = player.stats

    embed = discord.Embed(
        title = f'{player.display_name}\'s stats',
        colour = discord.Colour.blue()
    )

    embed.set_footer(text = 'Powered by www.rocketleaguestats.com')

    embed.set_thumbnail(url = avatar)
    embed.add_field(name = 'Wins', value = stats['wins'])
    embed.add_field(name = 'MVPs', value = stats['mvps'])
    embed.add_field(name = 'Shots', value = stats['shots'])
    embed.add_field(name = 'Goals', value = stats['goals'])
    embed.add_field(name = 'Assists', value = stats['assists'])
    embed.add_field(name = 'Saves', value = stats['saves'])

    await ctx.send(embed = embed)

@bot.command(name = 'rank')
async def rank(ctx, uid, platform = const.STEAM, season = 'all', playlist = 'all'):
    if platform != const.STEAM:
        platform = await get_platform(platform)

    player = await rlsclient.get_player(uid, platform)
    ranked = player.ranked_seasons
    plist = await rlsclient.get_playlists()
    tierlist = await rlsclient.get_tiers()
    pname = ''

    embed = discord.Embed(
        title = f'{player.display_name}\'s All Season\'s Stats',
        colour = discord.Colour.blue()
    )

    if season == 'all' and playlist == 'all':
        for season in ranked:
            embed.add_field(name = f"Season:", value = f"{season}", inline = False)
            for playlist in ranked[season]:
                for id in plist:
                    if id.id == int(playlist):
                        pname = id.name
                        break

                tier = tierlist[ranked[season][playlist][3]]
                if tier.name.lower() == 'unranked':
                    continue

                embed.add_field(name = pname, value = tier.name)
    elif season != 'all' and playlist == 'all':
        try:
            tmp = int(season)
        except:
            await ctx.send(f"Sorry, Season {season} is not a real season.")
            return
        embed.add_field(name = f"Season:", value = f"{season}", inline = False)
        for playlist in ranked[season]:
            for id in plist:
                if id.id == int(playlist):
                    pname = id.name
                    break

            tier = tierlist[ranked[season][playlist][3]]
            if tier.name.lower() == 'unranked':
                continue

            embed.add_field(name = pname, value = tier.name)
    elif season != 'all' and playlist != 'all':
        try:
            tmp = int(season)
            tmp = int(playlist)
        except:
            await ctx.send(f"Sorry, either your season or playlist is wrong.")
            return
        embed.add_field(name = f"Season:", value = f"{season}", inline = False)
        for id in plist:
            if id.id == int(playlist):
                pname = id.name
                break

        tier = tierlist[ranked[season][playlist][3]]

        embed.add_field(name = pname, value = tier.name)
    embed.set_footer(text = "Powered by Rocketleaguestats.com *disclaimer: RLS doesn't always"
                            " store all season data.")
    await ctx.send(embed = embed)

@bot.command(name = 'mutate')
async def mutate(ctx):
    embed = discord.Embed(
        title = 'Randomized Mutators',
        colour = discord.Colour.blue()
    )
    for key in mutators.data:
        mutate = random.choice(mutators.data[key])
        embed.add_field(name = key, value = mutate)
    await ctx.send(embed = embed)

@bot.command(name = 'fuck')
async def fuck(ctx):
    await bot.close()

if __name__ == '__main__':
    mutators = Pyson('mutators')

    with open('rlstoken.txt') as rlstoken:
        rlstoken = rlstoken.readline()

    rlsclient = rs.RLS_Client(rlstoken.strip())

    bot.loop.run_until_complete(bot.run(token.strip()))

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



#reaction role----------------------------------------------------

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
async def tank():
	await client.say('tank sucks dick!')
	
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
    await client.say(embed=embed)




#---------------------------------------------------

client.run(os.getenv('TOKEN'))
