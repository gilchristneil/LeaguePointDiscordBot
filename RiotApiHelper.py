import requests
import threading
import time


class RiotApi:
    def __init__(self, apiKey: str, cfg):
        self._apiKey = apiKey
        self._baseUrl = 'https://na1.api.riotgames.com/lol/'
        self._cfg = cfg

        @property
        def apiKey(self):
            return self._apiKey

        @property
        def baseUrl(self):
            return self._baseUrl

        @property
        def cfg(self):
            return self._cfg

    def getSummonerId(self, summonerName: str):
        """id(summonerId)"""
        requestUrl = f"{self._baseUrl}summoner/v4/summoners/by-name/{summonerName}"
        response = requests.get(
            requestUrl,
            headers={"X-Riot-Token": self._apiKey},
        )
        return response.json()['id']

    def findGame(self, summonerId: str):
        game = GameWatcher(self._apiKey, summonerId, self._baseUrl)

        while game._matchId == "":
            break
        print("found match?")
        return game._matchId

    def getActiveGame(self, summonerId: str):
        self.findGame(summonerId)
        requestUrl = f"{self._baseUrl}spectator/v4/active-games/by-summoner/{summonerId}"
        response = requests.get(
            requestUrl,
            headers={"X-Riot-Token": self._apiKey},
        )

        if response.status_code != 200:
            return False

        return response.json()

    def getHistoricMatch(self, matchId: str):
        requestUrl = f"{self._baseUrl}match/v4/matches/{matchId}"
        response = requests.get(
            requestUrl,
            headers={"X-Riot-Token": self._apiKey},
        )
        return response.json()


class GameWatcher:
    def __init__(self, apiKey: str, summonerId: str, baseUrl: str):

        self._apiKey = apiKey
        self._summonerId = summonerId
        self._matchId = ""
        self._baseUrl = baseUrl

        @property
        def matchId(self):
            return self._matchId

        self._timer = None
        self.interval = 1
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def pingSpectator(self):
        """ Get response Code from spectator API """
        requestUrl = f"{self._baseUrl}spectator/v4/active-games/by-summoner/{self._summonerId}"
        response = requests.get(
            requestUrl,
            headers={"X-Riot-Token": self._apiKey},
        )
        print(response)
        if response.status_code == 200:
            self.stop()
            self._matchId = response.json()['gameId']
            print("actually found the game :) ")

        else:
            print('TRYING AGAIN OKAY?')

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(
                self.next_call - time.time(), self.pingSpectator)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
