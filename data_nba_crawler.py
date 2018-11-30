import json
import requests
from bs4 import BeautifulSoup


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
for i in range(21800001, 21800002):
    url = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2018/scores/pbp/00{}_full_pbp.json".format(i)
    response = requests.get(url, headers=header)
    if response.status_code == 404:
        continue
    json_response = json.loads(response.text, encoding='ascii')
    date, teams = json_response['g']['gcode'].split('/')
    with open('data/{}_{}.txt'.format(date, teams), 'a+') as f:
        f.write(url + '\n')
        f.write(date + '\t' + teams + '\n')
        for quarter_info in json_response['g']['pd']:
            quarter = quarter_info['p']
            for event in quarter_info['pla']:
                f.write(str(dict((byteify(key), byteify(value)) for key, value in event.iteritems())) + '\n')