import discord
from discord.ext import commands
import random
import yaml
import MongoDbHelper
import RiotApiHelper

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.',
                   description="League Bot",
                   intents=intents)

with open('_config.yaml', 'r') as config:
    cfg = yaml.safe_load(config)

dbHelper = MongoDbHelper.DbHelper(cfg=cfg)
riotApi = RiotApiHelper.RiotApi(apiKey=cfg['riot']['apiKey'], cfg=cfg)


@bot.event
async def on_ready():
    print('bot is ready')


@bot.command(name="roll", description="Rolls a dice in NdN format, Ex: .roll 1d6")
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(name="register", description="Registers the summoner name to the discord users Display Name")
async def registerSummoner(ctx, summonerName: str):
    """Registers Discord Userto Summoner Name -> Needed for Leader Role"""
    try:
        id = riotApi.getSummonerId(summonerName)
        res = dbHelper.addSummoner(
            id, summonerName, ctx.message.author.display_name)
        if res == 1:
            await ctx.send(f"<@{ctx.message.author.id}> that summoner is already registered, please use edit command if you would like to transfer ownership")
        elif res == 2:
            await ctx.send(f"<@{ctx.message.author.id}> you are already registered to a summoner, please use edit command to transfer a summoner to you")
        else:
            await ctx.send(f"<@{ctx.message.author.id}> you were added to registry with summoner name {summonerName}")
    except Exception as e:
        await ctx.send(e)
        return


@bot.command(name="edit", description="Changes what summoner is attributed to your discord")
async def editSummoner(ctx, summonerName: str):
    """:param SummonerName """
    try:
        edit = dbHelper.editSummonerOwner(
            str(summonerName), str(ctx.message.author.display_name))
        if (edit.matched_count == 0):
            await ctx.send(f"<@{ctx.message.author.id}> I could not find that summoner.")
            return
        elif (edit.modified_count == 0):
            await ctx.send(f"<@{ctx.message.author.id}> I found the summoner but something went wrong!")
            return
        else:
            await ctx.send(f"<@{ctx.message.author.id}> the summoner {summonerName} is now yours!")
    except Except as e:
        await ctx.send(e)


@bot.command(name="watch", description="Tells the bot to watch your next game")
async def watchGame(ctx):
    """Tells Bot to watch next game of caller for points"""
    summonerId = dbHelper.getSummonerIdFromDiscordName(
        ctx.message.author.display_name)
    matchData = riotApi.getActiveGame(summonerId)
    if matchData == False:
        return
    redTeam = []
    blueTeam = []

    for player in matchData['participants']:
        if player["teamId"] == 100:
            redTeam.append(player['summonerName'])
        elif player["teamId"] == 200:
            blueTeam.append(player['summonerName'])
        userMatch = copy(cfg['db']['userMatchSchema'])
        userMatch = {
            'MatchId': matchData['gameId'],
            'SummonerId': player['summonerId'],
            'ChampionId': player['championId'],
            'ParticipantId': '',
            'TeamId': player["teamId"]
        }
        userMatchDocId = self._db.UserMatch.insert_one(userMatch).inserted_id
        return 0
    match = copy(cfg['db']['matchSchema'])
    match = {
        'MatchId': matchData['gameId'],
        'TeamBlue': blueTeam,
        'TeamRed': redTeam,
        'winner': ''
    }
    matchDocId = self._db.Match.insert_one(match).inserted_id
    return 0


@bot.command(name="stats", description="Displays your current stats")
async def displayStats(ctx):
    """Displays your points in the tournament"""
    return


@bot.command(name="commands", description="displays all available commands")
async def help(ctx):
    helpText = ""
    for command in bot.commands:
        helpText += f"{command}\n"
    await ctx.send(helpText)

bot.run('ODE0NjUzMTIyOTY1NDA1NzA4.YDg-2A.yzgF0rTRBtpM3wIAwNfpNinsWZ8')
