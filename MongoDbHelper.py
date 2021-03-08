
import pymongo as mongo
import yaml
from copy import copy


class DbHelper:
    def __init__(self, cfg):
        self._cfg = cfg
        self._db = self.dbInit()

        @property
        def cfn(self):
            return self._cfg

        @property
        def db(self):
            return self._db

    def dbInit(self,):
        _client = mongo.MongoClient(self._cfg['db']['cxn'])
        _db = _client.leaguetournamentbot
        return _db

    def doesSummonerExist(self, summonerName):
        """Returns Bool -> if summoner name is already claimed by a discord member"""
        user = self._db.User.count_documents(
            {'SummonerName': summonerName}, limit=1)
        return bool(user)

    def getSummonerIdFromDiscordName(self, discordName):
        summonerId = self._db.User.find_one(
            {'DiscordName': discordName})
        return summonerId

    def doesDiscordUserExist(self, discordName):
        """Returns Bool -> if discord member is already attributed to a summoner name"""
        user = self._db.User.count_documents(
            {'DiscordName': discordName}, limit=1)
        return bool(user)

    def getDiscordNameFromSummonerName(self, summonerName):
        """Returns the Discord name from query of summoner name -> used to setting up the game watch"""
        discordName = self._db.User.find_one(
            {'SummonerName': summonerName.upper()})
        return discordName

    def addSummoner(self, summonerId, summonerName, discordName):
        """Add Summoner to the database"""
        if (self.doesSummonerExist(summonerName)):
            return 1
        elif (self.doesDiscordUserExist(discordName)):
            return 2
        else:
            user = copy(self._cfg['db']['userSchema'])
            user = {
                'SummonerId': summonerId,
                'SummonerName': summonerName.upper(),
                'DiscordName': discordName,
                'Points': 0
            }
            summonerDocId = self._db.User.insert_one(user).inserted_id
            return 0

    def editSummonerOwner(self, summonerName, discordName):
        """Changes the owner of the particular summonerName"""
        editTrack = self._db.User.update_one({'SummonerName': summonerName.upper()}, {
            "$set": {'DiscordName': discordName}})
        return editTrack
