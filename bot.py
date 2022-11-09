import json
import os

import discord
import tweepy
from discord.ext import commands
from discord.ext.commands.errors import (CheckFailure, CommandNotFound,
                                         MissingRequiredArgument)

from tracker import number_following_stored, get_time

bot = commands.Bot(command_prefix="!", help_command=None, case_insensitive=True, intents=discord.Intents.all())

auth = tweepy.OAuthHandler('qi0FcmJWMv1T6x8WYhvD6M8d3', 'HI9gHHJNiTXwBWuJlsXzFUDjOhe2t7gBHXbptCNE1L9JvzhFU6')
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAADhdUQEAAAAAaMGUYLBUc9APzkNTXIGNCPpDyF4%3DSFWrzBewEaWgRqDssuvfsQsKjpPMx1zR55QJSWratpDSejEb2T")


# TODO AFFICHER CHAQUE TAG ET LES COMPTES TRACKÉS


#############################################################################################################

@bot.event
async def on_ready():
    print("Tracker Bot Ready ...")

#############################################################################################################

@bot.event
async def on_command_error(ctx, error):
    """Custom error handler, for the selected exceptions
    not appearing in the terminal, or sending msg when arg is mandatory"""

    if isinstance(error, MissingRequiredArgument):
        embed = discord.Embed(
            description="You need to specify something after the command !  :x:",
            color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: empty command')
        await ctx.reply(embed=embed)
    elif isinstance(error, (CheckFailure, CommandNotFound)):
        pass

@bot.check
async def globally_block_dms(ctx):
    """Preventing anyone to send DM to the Bot"""
    return ctx.guild is not None


def checkAuthorized(ctx):
    """Defining discord IDs authorized for
    admin commands"""
    return ctx.message.author.id in [
        828233789594927115,
        965594724276793474,
        147053194801971200,
        1007398137062760549
    ]

#############################################################################################################


@bot.command()
@commands.check(checkAuthorized)
async def spyTags(ctx):
    with open('db.json', 'r') as f:
        db = json.load(f)

    tags = '\n- '.join(sorted(set(db[user]['Tag'].upper() for user in db)))
    embed = discord.Embed(
        description=f"**Current Tags are:\n\n- {tags}**",
        color=discord.Colour.blue(),
        )
    
    return await ctx.reply(embed=embed)


@bot.command()
@commands.check(checkAuthorized)
async def spy(ctx, *args):
    
    if len(args) != 2:
        embed = discord.Embed(
        description="**You need to specify a Twitter username and a Tag with this command  :x:**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: track: missing tag')
        return await ctx.reply(embed=embed)
    
    username = args[0]
    tag = args[1]
        
    
    with open('db.json', 'r') as f:
        db = json.load(f)

    try:
        twitter_user = api.get_user(screen_name=username)
        
        user_id = twitter_user.id
        username = twitter_user.screen_name
        followers_count = twitter_user.followers_count
        friends_count = twitter_user.friends_count
        bio = twitter_user.description
        profile_picture = twitter_user.profile_image_url_https
        
    except tweepy.errors.NotFound as err:
        embed = discord.Embed(
        description=f"**{username} is not a valid Twitter username  :x:**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: track: @{username} is not a valid Twitter username')
        return await ctx.reply(embed=embed)
    
    except Exception as err:
        print(type(err))
    
    
    if str(user_id) in db.keys():
        embed = discord.Embed(
        description=f"**@{username} is already tracked !**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: track: @{username} is already tracked')
        return await ctx.reply(embed=embed)
    
    try:
        follows = client.get_users_following(id=user_id, max_results=number_following_stored)
        follows_id = [user.id for user in follows.data]
    
    except TypeError:
        embed = discord.Embed(
        description=f"**Could not get followers of @{username}, this account may be private ...**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: track: could not get @{username} followers')
        return await ctx.reply(embed=embed)
    
    db[user_id] = {
        "username": username,
        "Tag": tag,
        "follows": follows_id,
        "profile_picture": profile_picture,
    }

    with open('db.json', 'r+') as f:
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()

    
    embed = discord.Embed(
    title=f"**@{username}**",
    url=f'https://twitter.com/{username}',
    color=discord.Colour.blue(),
    )
    
    embed.set_thumbnail(url=profile_picture)
    embed.set_author(name="NEW USER TRACKED", icon_url="https://static.vecteezy.com/system/resources/previews/002/743/514/original/green-check-mark-icon-in-a-circle-free-vector.jpg")    
    
    embed.add_field(name="Tag", value=tag.upper(), inline=False)
    embed.add_field(name="Followers", value=followers_count, inline=False)
    embed.add_field(name="Following", value=friends_count, inline=False)
    embed.add_field(name="Bio", value=bio if bio else "/", inline=False)
    
    print(f'[{get_time()}] track: @{username} is now tracked')
    return await ctx.reply(embed=embed)
    


@bot.command()
@commands.check(checkAuthorized)
async def unSpy(ctx, arg):
    
    username = arg
    
    with open('db.json', 'r') as f:
        db = json.load(f)
    
    tracked_usernames = [db[user]['username'] for user in db.keys()]
    
    if username not in tracked_usernames:
        embed = discord.Embed(
        description=f"**@{username} is not tracked !**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] Error: untrack: @{username} is not tracked')
        return await ctx.reply(embed=embed)
    
    elif username in tracked_usernames:
        for user in db.keys():
            if db[user]['username'] == username:
                del db[user]
                break
        
        with open('db.json', 'w') as f:
            json.dump(db, f, indent=4)
        
        
        embed = discord.Embed(
        description=f"**@{username} is no longer tracked :white_check_mark:**",
        color=discord.Colour.blue(),
        )
        print(f'[{get_time()}] untrack: @{username} is no longer tracked')
        return await ctx.reply(embed=embed)



if not os.path.isfile('db.json'):
    with open('db.json', 'w+') as f:
        json.dump({}, f, indent=4)

bot.run("MTAzODEyNDUxODI2ODQ4NTcyMw.G30rEI.ZAIi-oi0s9ztR6QUEn8honbeNSQXwTi6xvDwHA")