import math
from bs4 import BeautifulSoup
from selenium import webdriver

fd_url = "https://sportsbook.fanduel.com/navigation/ncaab"
dk_url = "https://sportsbook.draftkings.com/leagues/basketball/88670771"

driver = webdriver.Chrome()

# This driver call is for chromium to work on Mitch's computer.
# driver = webdriver.Chrome('/Users/mitchellmiles/gambling/arbitrage/venv/lib/python3.9/site-packages/selenium/webdriver/chrome/chromedriver')

driver.get(dk_url)
page_source = driver.page_source
dk_soup = BeautifulSoup(page_source, "html.parser")
rows = dk_soup.find_all('tr')
dk_valids = {}
away = True
teams = []
ml = []
for row in rows[1:]:
    try:
        team = row.select('div.event-cell__name-text')[0].text
        odds = row.select('span.sportsbook-odds.american.no-margin')[0].text
        if away:
            away = False
            teams = [team]
            ml = [odds]
        else:
            away = True
            teams.append(team)
            ml.append(odds)
            if teams[0] > teams[1]:
                teams = teams[::-1]
                ml = ml[::-1]
            if ml[0] != '' and ml[1] != '':
                dk_valids[tuple(teams)] = tuple(ml)
    except:
        pass

driver.get(fd_url)
page_source = driver.page_source
soup = BeautifulSoup(page_source, "html.parser")
game_links = soup.select('a[href*=ncaa-basketball]')
fd_valids = {}
odd = True
for game_link in game_links:
    try:
        if odd:
            odd = False
            teams = game_link.get('title').split(' @ ')
            game = game_link.parent
            game_inner = game.contents[1]
            away = game_inner.contents[0].contents[1].contents[0].contents[0].text
            home = game_inner.contents[1].contents[1].contents[0].contents[0].text
            ml = [away, home]
            if teams[0] > teams[1]:
                teams = teams[::-1]
                ml = ml[::-1]
            if ml[0] != '' and ml[1] != '':
                fd_valids[tuple(teams)] = tuple(ml)
        else:
            odd = True
            pass
    except:
        pass
driver.close()


def check_arb(dk_game, fd_game):
    dk_odds_1 = dk_valids[dk_game][0]
    dk_odds_2 = dk_valids[dk_game][1]
    fd_odds_1 = fd_valids[fd_game][0]
    fd_odds_2 = fd_valids[fd_game][1]
    if dk_odds_1[0] == '+':
        dk_decimal_1 = 1+int(dk_odds_1[1:])/100
    else:
        dk_decimal_1 = 1+100/int(dk_odds_1[1:])
    if dk_odds_2[0] == '+':
        dk_decimal_2 = 1+int(dk_odds_2[1:])/100
    else:
        dk_decimal_2 = 1+100/int(dk_odds_2[1:])
    if fd_odds_1[0] == '+':
        fd_decimal_1 = 1+int(fd_odds_1[1:])/100
    else:
        fd_decimal_1 = 1+100/int(fd_odds_1[1:])
    if fd_odds_2[0] == '+':
        fd_decimal_2 = 1+int(fd_odds_2[1:])/100
    else:
        fd_decimal_2 = 1+100/int(fd_odds_2[1:])
    if 1/fd_decimal_1 + 1/dk_decimal_2 < 1:
        return {"fd": (fd_game[0], 1 / fd_decimal_1), "dk": (dk_game[1], 1 / dk_decimal_2)}
    if 1/fd_decimal_2 + 1/dk_decimal_1 < 1:
        return {"fd": (fd_game[1], 1/fd_decimal_2), "dk": (dk_game[0], 1/dk_decimal_1)}
    return None



unit = 100

for dk_game in dk_valids:
    fd_game = [(team1, team2) for (team1, team2) in fd_valids if (team1 == dk_game[0] or team2 == dk_game[1])]
    if len(fd_game) > 0:
        arb = check_arb(dk_game, fd_game[0])
        if arb:
            print(f"Bet ${round(unit*arb['fd'][1], 2)} on {arb['fd'][0]} on Fanduel @ {math.trunc(-100/(1/arb['fd'][1]-1)) if 1/arb['fd'][1] < 2 else '+'+str(math.trunc((1/arb['fd'][1]-1)*100))} and ${round(unit*arb['dk'][1], 2)} on {arb['dk'][0]} on DraftKings @ {math.trunc(-100/(1/arb['dk'][1]-1)) if 1/arb['dk'][1] < 2 else '+'+str(math.trunc((1/arb['dk'][1]-1)*100))} to profit ${round(unit-(unit*arb['fd'][1]+unit*arb['dk'][1]), 2)}")