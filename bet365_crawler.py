from __future__ import absolute_import
from __future__ import print_function

from time import sleep
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

waiting_time = 30
option = webdriver.ChromeOptions()
option.add_argument('headless')

# driver = webdriver.Chrome(chrome_options=option)
driver = webdriver.Chrome()
driver.get('https://www.bet365.com.cy/en/')

match_status = dict()
round = 0
driver.get('https://www.bet365.com.cy/#/AC/B18/C20604387/D48/E1453/F10/')

while True:
    print ("round {}".format(round))
    round += 1

    driver.refresh()
    try:
        element = WebDriverWait(driver, waiting_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sl-CouponParticipantGameLineTwoWay_NameText"))
        )
    except selenium.common.exceptions.TimeoutException:
        print ("Time Loading Exception !!!")
    finally:
        sleep(2.5)

    try:
        matches = driver.find_elements_by_class_name("sl-CouponParticipantGameLineTwoWay")
        times = driver.find_elements_by_class_name("sl-CouponParticipantGameLineTwoWay_Time")
        teams = driver.find_elements_by_class_name("sl-CouponParticipantGameLineTwoWay_NameText")
        spreads = driver.find_elements_by_class_name("gl-ParticipantCentered_Name")
        spread_odds = driver.find_elements_by_class_name("gl-ParticipantCentered_Odds")
        scores = driver.find_elements_by_class_name('pi-ScoreVariantDefault')
        num_match = len(times)

        matches = [match.text.encode('utf-8') for match in matches]
        times = [matches[i].split(' ')[0] for i in range(0, 2 * num_match, 2)]

        ongoing = False
        for tt in times:
            if 'Q' in tt:
                ongoing = True
                break
        if not ongoing:
            continue

        teams = [[teams[i].text.encode('utf-8'), teams[i + 1].text.encode('utf-8')] for i in range(0, num_match * 2, 2)]
        spread_odd = [[[spreads[i].text.encode('utf-8'), spread_odds[i].text.encode('utf-8')], [spreads[i + 1].text.encode('utf-8'), spread_odds[i + 1].text.encode('utf-8')]] for i in range(0, num_match * 4, 2)]
        spread = spread_odd[0: num_match]
        total = spread_odd[num_match: num_match * 2]
        money_line = [[spread_odds[i].text.encode('utf-8'), spread_odds[i + 1].text.encode('utf-8')] for i in range(num_match * 4, num_match * 6, 2)]
        scores = [[int(scores[i].text), int(scores[i + 1].text)] if i < len(scores) - 1 else [0, 0] for i in range(0, 2 * num_match, 2)]

    except selenium.common.exceptions.StaleElementReferenceException:
        continue

    cur_match_statuses = [[times[i], teams[i][0], teams[i][1], scores[i][0], scores[i][1], spread[i][0][0], spread[i][0][1], spread[i][1][0], spread[i][1][1], total[i][0][0], total[i][0][1], total[i][1][0], total[i][1][1], money_line[i][0], money_line[i][1]] for i in range(num_match)]
    cur_match_teams = {(teams[i][0], teams[i][1]) for i in range(num_match)}

    for cur_match_status in cur_match_statuses:
        match_teams = (cur_match_status[1], cur_match_status[2])
        prev_match_status = match_status.get(match_teams, None)
        if prev_match_status is None or (cur_match_status[1:] != prev_match_status[1:] and cur_match_status[3] >= prev_match_status[3] and cur_match_status[4] >= prev_match_status[4]):
            print(prev_match_status)
            print(cur_match_status)
            print ("update")
            with open('games/{} {}.txt'.format(cur_match_status[1], cur_match_status[2]), 'a+') as f:
                for st in cur_match_status:
                    f.write(str(st) + '\t')
                f.write('\n')
            match_status[match_teams] = cur_match_status
    for match_teams in match_status.keys():
        if match_teams not in cur_match_teams:
            match_status.pop(match_teams)
    sleep(random.uniform(0.5, 2.0))

