import math
from bs4 import BeautifulSoup
from selenium import webdriver


fd_url = "https://sportsbook.fanduel.com/navigation/ncaab"
dk_url = "https://sportsbook.draftkings.com/leagues/basketball/88670771"


def get_odds():
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
    return fd_valids, dk_valids


def check_arb(fd_game, dk_game, fd_valids, dk_valids):
    #Get American odds from dictionaries
    dk_odds_1 = dk_valids[dk_game][0]
    dk_odds_2 = dk_valids[dk_game][1]
    fd_odds_1 = fd_valids[fd_game][0]
    fd_odds_2 = fd_valids[fd_game][1]
    #Convert American odds to decimal odds
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
    #Check if combined implied probabilities sum to less than 1, AKA books disagree strongly enough that arbitrage bets can be placed for profit
    if 1/fd_decimal_1 + 1/dk_decimal_2 < 1:
        return {"fd": (fd_game[0], 1 / fd_decimal_1), "dk": (dk_game[1], 1 / dk_decimal_2)}
    if 1/fd_decimal_2 + 1/dk_decimal_1 < 1:
        return {"fd": (fd_game[1], 1/fd_decimal_2), "dk": (dk_game[0], 1/dk_decimal_1)}
    return None


def check_arb_rounded(fd_game, dk_game, unit, fd_valids, dk_valids):
    # Get American odds from dictionaries
    dk_odds_1 = dk_valids[dk_game][0]
    dk_odds_2 = dk_valids[dk_game][1]
    fd_odds_1 = fd_valids[fd_game][0]
    fd_odds_2 = fd_valids[fd_game][1]
    # Convert American odds to decimal odds
    if dk_odds_1[0] == '+':
        dk_decimal_1 = 1 + int(dk_odds_1[1:]) / 100
    else:
        dk_decimal_1 = 1 + 100 / int(dk_odds_1[1:])
    if dk_odds_2[0] == '+':
        dk_decimal_2 = 1 + int(dk_odds_2[1:]) / 100
    else:
        dk_decimal_2 = 1 + 100 / int(dk_odds_2[1:])
    if fd_odds_1[0] == '+':
        fd_decimal_1 = 1 + int(fd_odds_1[1:]) / 100
    else:
        fd_decimal_1 = 1 + 100 / int(fd_odds_1[1:])
    if fd_odds_2[0] == '+':
        fd_decimal_2 = 1 + int(fd_odds_2[1:]) / 100
    else:
        fd_decimal_2 = 1 + 100 / int(fd_odds_2[1:])
    # Check if combined implied probabilities sum to less than 1, AKA books disagree strongly enough that arbitrage bets can be placed for profit
    if 1 / fd_decimal_1 + 1 / dk_decimal_2 < 1:
        bet1 = (1 / fd_decimal_1) * unit
        bet2 = (1 / dk_decimal_2) * unit
        if bet2 > bet1:
            rounded1 = math.floor(bet1)
            rounded2 = math.floor(((rounded1 / bet1) * bet2))
        else:
            rounded2 = math.floor(bet2)
            rounded1 = math.floor((rounded2 / bet2) * bet1)
        if (rounded1*fd_decimal_1 - rounded1 - rounded2 > 0) and (rounded2*dk_decimal_2 - rounded1 - rounded2 > 0):
            return {'fd': (fd_valids[fd_game][0], fd_valids[fd_game][0], fd_decimal_1, rounded1), 'dk': (dk_valids[dk_game][1], dk_valids[dk_game][1], dk_decimal_2, rounded2)}
    if 1 / fd_decimal_2 + 1 / dk_decimal_1 < 1:
        bet1 = (1 / fd_decimal_2) * unit
        bet2 = (1 / dk_decimal_1) * unit
        if bet1 > bet2:
            rounded2 = math.floor(bet2)
            rounded1 = math.floor((rounded2 / bet2) * bet1)
        else:
            rounded1 = math.floor(bet1)
            rounded2 = math.floor((rounded1 / bet1) * bet2)
        if (rounded2*dk_decimal_1 - rounded1 - rounded2 > 0) and (rounded1*fd_decimal_2 - rounded1 - rounded2 > 0):
            return {'fd': (fd_valids[fd_game][1], fd_valids[fd_game][1], fd_decimal_2, rounded1), 'dk': (dk_valids[dk_game][0], dk_valids[dk_game][0], dk_decimal_1, rounded2)}
    return None


def run_exact(unit):
    fd_valids, dk_valids = get_odds()
    fd_valids[('Conor', 'Mitch')] = ('-300', '+1000')
    dk_valids[('Conor', 'Mitch')] = ('-150', '+330')
    for dk_game in dk_valids:
        fd_game = [(team1, team2) for (team1, team2) in fd_valids if (team1 == dk_game[0] or team2 == dk_game[1])]
        if len(fd_game) > 0:
            #If both books have the same team, we check if there is an arbitrage opportunity. We used to check if both teams matched in case a team was on the page twice, but this is a rare case, and many teams are abbreviated differently between the two books.
            arb = check_arb(fd_game[0], dk_game, fd_valids, dk_valids)
            if arb:
                #If there is an opportunity for guaranteed profit at the time the odds were scraped, gives you information on how much to bet on each book
                print(f"Bet ${round(unit*arb['fd'][1], 2)} on {arb['fd'][0]} on Fanduel @{math.trunc(-100/(1/arb['fd'][1]-1)) if 1/arb['fd'][1] < 2 else '+'+str(math.trunc((1/arb['fd'][1]-1)*100))} and ${round(unit*arb['dk'][1], 2)} on {arb['dk'][0]} on DraftKings @{math.trunc(-100/(1/arb['dk'][1]-1)) if 1/arb['dk'][1] < 2 else '+'+str(math.trunc((1/arb['dk'][1]-1)*100))} to profit ${round(unit-(unit*arb['fd'][1]+unit*arb['dk'][1]), 2)}")

def run_round(unit):
    fd_valids, dk_valids = get_odds()
    fd_valids[('Conor', 'Mitch')] = ('-300', '+1000')
    dk_valids[('Conor', 'Mitch')] = ('-150', '+330')
    for dk_game in dk_valids:
        fd_game = [(team1, team2) for (team1, team2) in fd_valids if (team1 == dk_game[0] or team2 == dk_game[1])]
        if len(fd_game) > 0:
            # If both books have the same team, we check if there is an arbitrage opportunity. We used to check if both teams matched in case a team was on the page twice, but this is a rare case, and many teams are abbreviated differently between the two books.
            arb = check_arb_rounded(fd_game[0], dk_game, unit, fd_valids, dk_valids)
            if arb:
                print(f"Bet ${arb['fd'][3]} on {arb['fd'][0]} on Fanduel @{arb['fd'][1]} and ${arb['dk'][3]} on {arb['dk'][0]} on DraftKings @{arb['dk'][1]} to profit ${round(min(arb['fd'][2] * arb['fd'][3] - arb['fd'][3] - arb['dk'][3], arb['dk'][2] * arb['dk'][3] - arb['fd'][3] - arb['dk'][3]), 2)}")


#run_exact(100)
run_round(100)
