import discord
import asyncio
import json
import pdb
import requests
from discord.ext import commands
from pubg_python import PUBG, Shard, exceptions
import bot_utils
import sys
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

description = """>>>>>Mr. Pubg-bot<<<<<
This bot will be your go-to pubg information buddy! Look at these neat commands:
All commands begin with "!"

"""
bot = commands.Bot(command_prefix='!', description=description)

#DATA = json.load(open('bot_info.json'))
#PUBG_CLIENT = PUBG(DATA["PUBG_API_KEY"], Shard.PC_NA)
PUBG_CLIENT = PUBG(os.environ["PUBG_API_KEY"], Shard.PC_NA)

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

##################################
#                                #
#                                #
#        Matches commands        #
#                                #
#                                #
##################################
@bot.group(pass_context=True)
@asyncio.coroutine
def matches(ctx):
    """'Provides match data for the last 5 matches for the in-game name provided.
    By providing a date it will get all matches that day.'
    """
    if ctx.invoked_subcommand is None:
        try:
            logging.info(">>>>>>>>>>>>>searching for player %s<<<<<<<<<<<<<<<<<<<", ctx.subcommand_passed)
            player = PUBG_CLIENT.players().filter(player_names=[ctx.subcommand_passed])
            player = player[0]
            logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
        except exceptions.NotFoundError:
            yield from bot.say('That player does not exist. Make sure the name is identical')
            return
        
        #TODO: Make sure that if there are not 5 matches it only displays available matches
        match_dict = {}
        logging.info(">>>>>>>>>>>>>printing five matches<<<<<<<<<<<<<<<<<<<")
        embed = discord.Embed(title="React to the match you wish to see data for:",
                                colour=discord.Colour(14066432))

        #displays a list of matches
        emoji_list = bot_utils.get_random_emoji_list()
        for idx, match in enumerate(player.matches[:len(emoji_list)]):
            match_dict[emoji_list[idx]] = match.id
            embed.add_field(name=emoji_list[idx] + ': ', value=match.id, inline=False)
        yield from bot.say(embed=embed)

        logging.info(">>>>>>>>>>>>>waiting for reaction from %s<<<<<<<<<<<<<<<<<<<", ctx.message.author)
        res = yield from bot.wait_for_reaction(user=ctx.message.author, timeout=20000) #Waits for 10000ms (maybe?) for a user to react.
        logging.info("reaction occurred from %s", ctx.message.author)

        match = PUBG_CLIENT.matches().get(match_dict[res.reaction.emoji]) #splits message and pulls id
        
        yield from bot.say("Let me get " + match_dict[res.reaction.emoji] + " match's data.")
        embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT, False)
        yield from bot.say(embed=embed)

@matches.command(name='last', pass_context=True)
@asyncio.coroutine
def _last(ctx, ign : str, number_of_matches : int):
    """'EX: <!matches last Jabronious 10> - This will provide 10 matches for Jabronious
    """
    try:
        logging.info(">>>>>>>>>>>>>searching for player %s<<<<<<<<<<<<<<<<<<<", ign)
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
        logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return

    match_dict = {}
    logging.info(">>>>>>>>>>>>>printing " + str(number_of_matches) + " matches<<<<<<<<<<<<<<<<<<<")
    embed = discord.Embed(title="React to the match you wish to see data for:",
                            colour=discord.Colour(14066432))

    #displays a list of matches
    emoji_list = bot_utils.get_random_emoji_list(number_of_matches)
    for idx, match in enumerate(player.matches[:len(emoji_list)]):
        match_dict[emoji_list[idx]] = match.id
        embed.add_field(name=emoji_list[idx] + ': ', value=match.id, inline=False)
    yield from bot.say(embed=embed)

    logging.info(">>>>>>>>>>>>>waiting for reaction from %s<<<<<<<<<<<<<<<<<<<", ctx.message.author)
    res = yield from bot.wait_for_reaction(user=ctx.message.author, timeout=20000) #Waits for 10000ms (maybe?) for a user to react.
    logging.info("reaction occurred from %s", ctx.message.author)

    match = PUBG_CLIENT.matches().get(match_dict[res.reaction.emoji]) #splits message and pulls id

    yield from bot.say("Let me get " + match_dict[res.reaction.emoji] + " match's data.")
    embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT, False)
    yield from bot.say(embed=embed)

@matches.command(name='latest', pass_context=True)
@asyncio.coroutine
def _latest(ctx, ign : str, name='latest-match'):
    """'latest <in-game name>. Will provide stats from the most recent match.'"""
    try:
        logging.info(">>>>>>>>>>>>>searching for player %s, subcommand: %s<<<<<<<<<<<<<<<<<<<", ign, ctx.subcommand_passed)
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
        logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return
    match = PUBG_CLIENT.matches().get(player.matches[0].id)
    
    yield from bot.say("Let me get that match's data.")
    embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT)
    yield from bot.say(embed=embed)

@matches.command(name='date', pass_context=True)
@asyncio.coroutine
def _date(ctx, ign : str, *date : int):
    #TODO: ADD LOGGING
    """'date <in-game name> <date> : Format the MM DD YYYY EX: 04 03 2018'"""
    date = datetime(year=date[2], month=date[1], day=date[0])
    matches = PUBG_CLIENT.matches().filter(
        created_at_start=str(date),
        created_at_end=str(date + timedelta(days=1))
    )
    yield from bot.say("This feature is not available yet.")

@matches.error
@asyncio.coroutine
def ign_error(error, ctx):
    logging.debug('***********Invoked Command: ' + ctx.invoked_with + ", Invoked Subcommand: " + str(ctx.invoked_subcommand) + "(" + ctx.subcommand_passed + "), "
                    + "Error: " + str(error) + ", Message author: " + ctx.message.author.name + ", Message: " + ctx.message.content + "***********")
    yield from bot.say("Something Happened, OH NO!! Don't Worry, you just need to make sure you have entered the command correct" + 
        "or the player's in-game name is identical")

##################################
#                                #
#                                #
#        Admin commands          #
#                                #
#                                #
##################################
@bot.command(pass_context=True, hidden=True)
@asyncio.coroutine
def restart(ctx):
    message = ctx.message
    logging.info("Restart >>>INITIATED<<< in server(" + message.author.server.name + ") by " + message.author.name)
    if message.author.server.id == '422922120608350208' and message.author.id == '304806386536153088' or message.author.id == '176648415428476930':
        yield from bot.send_message(message.channel, 'Restarting')
        logging.info("Restart >>>SUCCESSFUL<<< in server(" + message.author.server.name + ") by " + message.author.name)
        python = sys.executable
        os.execl(python, python, * sys.argv)
    logging.info("Restart >>>FAILED<<< in server(" + message.author.server.name + ") by " + message.author.name)

#bot.run(DATA['TOKEN'])
bot.run(os.environ['TOKEN'])