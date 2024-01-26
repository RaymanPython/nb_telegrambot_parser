import requests                                                                                                                                     
import json
import collections

def GetData(game_id: str):
    # {date} - {time} - {city} - {arena name} - {team1name} : {team2name}
    tres = collections.namedtuple("GameInfo", ['date', 'time', 'TimeMSK', 'arena', 'team1', 'team2', 'jury'], defaults=['', '', '', '', '', '', []])
    res = tres()
    data = json.loads(requests.get(f"https://reg.infobasket.su/Widget/GetOnline/{game_id}?format=json&lang=ru").text)
    # Try to get jury
    if 'OnlineStarts' in data:
        for S in data['OnlineStarts']:
            if S['StartType'] == 4:
                res.jury.append(S['PersonName2'])
    if 'GameDate' in data:
        res = res._replace(date=data['GameDate'])
    if 'GameTime' in data:
        res = res._replace(time=data['GameTime'])
    if 'GameTimeMsk' in data:
        res = res._replace(TimeMSK=data['GameTimeMsk'])
    if 'Online' in data and 'Venue2' in data['Online']:
        res = res._replace(arena=data['Online']['Venue2'])
    
    res = res._replace(team1=data['GameTeams'][0]['TeamName']['CompTeamNameRu'])
    res = res._replace(team2=data['GameTeams'][1]['TeamName']['CompTeamNameRu'])
    return res

def data_for_url(url):
    return GetData(url.split('=')[-1])

if __name__ == '__main__':
    print(data_for_url('http://neva-basket.ru/game?gameId=785272'))