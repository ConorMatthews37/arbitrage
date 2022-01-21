from bs4 import BeautifulSoup
from selenium import webdriver

fd_url = "https://sportsbook.fanduel.com/navigation/ncaab"
dk_url = "https://sportsbook.draftkings.com/leagues/basketball/88670771"

driver = webdriver.Chrome()

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


def check_arb(game):
    dk_odds_1 = dk_valids[game][0]
    dk_odds_2 = dk_valids[game][1]
    fd_odds_1 = fd_valids[game][0]
    fd_odds_2 = fd_valids[game][1]
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
        return {"fd": (game[0], 1 / fd_decimal_1), "dk": (game[1], 1 / dk_decimal_2)}
    if 1/fd_decimal_2 + 1/dk_decimal_1 < 1:
        return {"fd": (game[1], 1/fd_decimal_2), "dk": (game[0], 1/dk_decimal_1)}
    return None



unit = 100

for game in dk_valids:
    if game in fd_valids:
        arb = check_arb(game)
        if arb:
            print(f"Bet {round(unit*arb['fd'][1], 2)} on {arb['fd'][0]} on Fanduel @ {-100/(1/arb['fd'][1]-1) if 1/arb['fd'][1] < 2 else (1/arb['fd'][1]-1)*100} and {unit*arb['dk'][1]} on {arb['dk'][0]} on DraftKings @ {-100/(1/arb['dk'][1]-1) if 1/arb['dk'][1] < 2 else (1/arb['dk'][1]-1)*100} to profit {unit-(unit*arb['fd'][1]+unit*arb['dk'][1])}")