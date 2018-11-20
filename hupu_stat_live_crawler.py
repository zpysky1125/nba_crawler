# coding: utf-8
import requests
import random
from bs4 import BeautifulSoup
from time import sleep

status_dict = {}
while True:
    header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    entrance = requests.get("https://nba.hupu.com/games", headers=header)
    entrance_soup = BeautifulSoup(entrance.text, 'html.parser')
    matches = entrance_soup.find_all('div', class_='list_box')

    for match in matches:
        status = match.select('div[class^="team"] span[class="b"]')[0].get_text().strip()
        if status == '已结束'.decode('utf-8'):
            teams = tuple([team.get_text().encode('utf-8') for team in match.select('div[class="txt"] span a')])
            if status_dict.has_key(teams):
                status_dict.pop(teams)
            continue
        if '未开始'.decode('utf-8') in status:
            continue

        name_scores = match.select('div[class="txt"]')
        link = match.select('div[class^="table_choose"] a[class="d"]')
        link = link[0]['href']
        stat = requests.get(link, headers=header)
        stat_soup = BeautifulSoup(stat.text, 'html.parser')
        tt = stat_soup.select('div[class^="team_num"]')
        if len(tt) == 0:
            continue
        cur_match_status = [tt.encode('utf-8')[0].get_text()]
        tables = stat_soup.select('table[id]')

        ns = []
        for name_score in name_scores:
            name = name_score.select('span > a')[0].get_text().encode('utf-8')
            score = name_score.select('span[class^="num "]')[0].get_text().encode('utf-8')
            ns += [name, score]

        cur_match_status += [ns[0], ns[2], ns[1], ns[3]]

        for table in tables:
            team_status = []
            trs = table.select('tr')
            for tr in trs:
                tds = tr.select('td')
                stat = [td.get_text().replace('\n', '').encode('utf-8') for td in tds]
                if len(stat[1]) > 0:
                    team_status.append(stat)
            cur_match_status.append(team_status)

        match_teams = (cur_match_status[1], cur_match_status[2])
        prev_match_status = status_dict.get(match_teams, None)
        if prev_match_status is None or (cur_match_status != prev_match_status):
            status_dict[match_teams] = cur_match_status
            print (prev_match_status)
            print (cur_match_status)
            print ("update")

            with open('hupu/{} {}.txt'.format(match_teams[0], match_teams[1]), 'a+') as f:
                for st in cur_match_status[:5]:
                    f.write(st + '\t')
                for team_status in cur_match_status[5:]:
                    for person_status in team_status:
                        f.write('\n')
                        for st in person_status:
                            f.write(st + '\t')
                f.write('\n\n')

    sleep(random.uniform(0.5, 2.0))
