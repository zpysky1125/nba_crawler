from __future__ import absolute_import
from __future__ import print_function

from time import sleep
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


waiting_time = 30
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome()
driver.get('https://www.bet365.com.cy/en/')
driver.get('https://www.bet365.com.cy/#/IP/')

match_status = dict()
round = 0

while True:
    driver.refresh()
    print ("round {}".format(round))
    round += 1

    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ipo-ClassificationBarButtonBase"))
        )
    except selenium.common.exceptions.TimeoutException:
        print("Time Loading Exception !!!")
    finally:
        sleep(2.5)

    names = driver.find_elements_by_class_name("ipo-ClassificationBarButtonBase")
    for name in names:
        if name.text == "Basketball":
            ActionChains(driver).click(name).perform()

    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ipo-CompetitionRenderer"))
        )
    except selenium.common.exceptions.TimeoutException:
        print ("Time Loading Exception !!!")
    finally:
        sleep(2.5)

    try:
        competition_render = driver.find_element_by_class_name("ipo-CompetitionRenderer")
        game_renders = competition_render.find_elements_by_class_name("ipo-Competition")
        nba_render = None
        for render in game_renders:
            render_name_div = render.find_element_by_class_name("ipo-CompetitionButton_NameLabel")
            if render_name_div.text == "NBA":
                nba_render = render

        if not nba_render:
            sleep(random.uniform(0.5, 2.0))
            continue

        games = nba_render.find_elements_by_class_name("ipo-Fixture")

        cur_match_statuses = []
        cur_match_teams = []

        for game in games:
            time_team_score = game.find_element_by_class_name("ipo-Fixture_ScoreDisplay")
            spread_total_money_line = game.find_element_by_class_name("ipo-MainMarkets")
            time_1 = time_team_score.find_element_by_class_name("ipo-InPlayTimer").text
            time_2 = time_team_score.find_element_by_class_name("ipo-PeriodInfo").text
            teams = [team.text for team in time_team_score.find_elements_by_class_name("ipo-TeamStack_Team")]
            scores = [score.text for score in time_team_score.find_elements_by_class_name("ipo-TeamPoints_TeamScore")]

            spreads_div, totals_div, money_lines_div = spread_total_money_line.find_elements_by_class_name("ipo-MainMarketRenderer")
            spreads = [spread.text for spread in spreads_div.find_elements_by_class_name("gl-ParticipantCentered_Handicap")]
            spread_odds = [odd.text for odd in spreads_div.find_elements_by_class_name("gl-ParticipantCentered_Odds")]
            totals = [total.text for total in totals_div.find_elements_by_class_name("gl-ParticipantCentered_Handicap")]
            total_odds = [odd.text for odd in totals_div.find_elements_by_class_name("gl-ParticipantCentered_Odds")]
            money_lines = [money_line.text for money_line in money_lines_div.find_elements_by_class_name("ipo-MainMarketRenderer_BlankParticipant ")]

            if len(teams) < 2:
                continue
            scores = scores if len(scores) == 2 else [0, 0]
            spreads = spreads if len(spreads) == 2 else ['', '']
            spread_odds = spread_odds if len(spread_odds) == 2 else ['', '']
            totals = totals if len(totals) == 2 else ['', '']
            total_odds = total_odds if len(total_odds) == 2 else ['', '']
            money_lines = money_lines if len(money_lines) == 2 else ['', '']

            cur_match_status = [time_2+time_1, teams[0], teams[1], scores[0], scores[1], spreads[0], spread_odds[0], spreads[1], spread_odds[1], totals[0], total_odds[0], totals[1], total_odds[1], money_lines[0], money_lines[1]]
            cur_match_statuses.append(cur_match_status)
            cur_match_teams.append((cur_match_status[1], cur_match_status[2]))

        for cur_match_status in cur_match_statuses:
            match_teams = (cur_match_status[1], cur_match_status[2])
            prev_match_status = match_status.get(match_teams, None)
            if prev_match_status is None or (cur_match_status[1:] != prev_match_status[1:] and cur_match_status[3] >= prev_match_status[3] and cur_match_status[4] >= prev_match_status[4]):
                print (prev_match_status)
                print (cur_match_status)
                print ("update")
                with open('games_2/{} {}.txt'.format(cur_match_status[1], cur_match_status[2]), 'a+') as f:
                    for st in cur_match_status:
                        f.write(str(st) + '\t')
                    f.write('\n')
                match_status[match_teams] = cur_match_status

        for match_teams in match_status.keys():
            if match_teams not in cur_match_teams:
                match_status.pop(match_teams)

    except selenium.common.exceptions.StaleElementReferenceException:
        continue

    sleep(random.uniform(0.5, 2.0))

