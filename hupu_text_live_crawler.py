# coding: utf-8
import requests
import random
import sys
from bs4 import BeautifulSoup
from time import sleep

date = sys.argv[1]

status_dict = {}

header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
entrance = requests.get("https://nba.hupu.com/games" + '/' + date, headers=header)
entrance_soup = BeautifulSoup(entrance.text, 'html.parser')
matches = entrance_soup.find_all('div', class_='list_box')

for match in matches:
    name_scores = match.select('div[class="txt"]')
    link = match.select('div[class^="table_choose"] a[class="b"]')
    link = link[0]['href']

    text = requests.get(link, headers=header)
    text_soup = BeautifulSoup(text.text, 'html.parser')
    cur_match_texts = []

    ns = []
    for name_score in name_scores:
        name = name_score.select('span > a')[0].get_text().encode('utf-8')
        score = name_score.select('span[class^="num "]')[0].get_text().encode('utf-8')
        ns += [name, score]

    with open('lives/{} {} {}.txt'.format(date, ns[0], ns[2]), 'a+') as f:
        for team_score in [ns[0], ns[2], ns[1], ns[3]]:
            f.write(team_score + '\t')
        f.write('\n')
        table = text_soup.select('div[class$="table_overflow"] table')[0]
        for tr in table.select('tr'):
            for td in tr.select('td'):
                f.write(td.get_text().strip().encode('utf-8') + '\t')
            f.write('\n')
        f.write('\n')

