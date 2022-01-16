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
            dk_valids[frozenset(teams)] = (tuple(teams), tuple(ml))
    except:
        pass

'''
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
            lines = game.select('div:nth-of-type(1)')
            print(lines)
            for line in lines:
                pass
                #2nd child home
                    # 2nd child ML
                        # 1st child
                            # 1st child
                                # text
        else:
            odd = True
            pass
    except:
        pass
        
'''
