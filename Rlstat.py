import discord
from discord.ext import commands
import rocket_snake as rs
from rocket_snake import constants as const
from pyson import Pyson

import random

bot = commands.Bot(command_prefix = 'RL!')

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

    # get discord token
    with open('token.txt') as token:
        token = token.readline()

    with open('rlstoken.txt') as rlstoken:
        rlstoken = rlstoken.readline()

    rlsclient = rs.RLS_Client(rlstoken.strip())

    bot.loop.run_until_complete(bot.run(token.strip()))
