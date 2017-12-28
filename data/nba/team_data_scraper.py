import time
import bs4
import requests
import pandas as pd
import numpy as np


TEAMS = [
    "ATL",
    "BOS",
    "CHA",
    "CHI",
    "CLE",
    "DAL",
    "DEN",
    "DET",
    "GSW",
    "HOU",
    "IND",
    "LAC",
    "LAL",
    "MEM",
    "MIA",
    "MIL",
    "MIN",
    "NJN",
    "NOH",
    "NYK",
    "OKC",
    "ORL",
    "PHI",
    "PHO",
    "POR",
    "SAC",
    "SAS",
    "TOR",
    "UTA",
    "WAS"
]
URL = "https://www.basketball-reference.com/teams/{}/"
STR_FIELDS = [
    "lg_id",
    "team_id",
    "avg_ht"
]
OPP_FIELDS_SKIP = ['lg_id', 'team_id', "wins", "losses", "rank_team", "g", "mp"]
STATS = [
    "lg_id",
    "team_id",
    "wins",
    "losses",
    "srs",
    "pace",
    "pace_rel",
    "off_rtg",
    "off_rtg_rel",
    "def_rtg",
    "def_rtg_rel",
    "rank_team",
    "avg_age",
    "avg_ht",
    "avg_wt",
    "g",
    "mp",
    "fg",
    "fga",
    "fg_pct",
    "fg3",
    "fg3a",
    "fg3_pct",
    "fg2",
    "fg2a",
    "fg2_pct",
    "ft",
    "fta",
    "ft_pct",
    "orb",
    "drb",
    "trb",
    "ast",
    "stl",
    "blk",
    "tov",
    "pf",
    "pts",
    "opp_fg",
    "opp_fga",
    "opp_fg_pct",
    "opp_fg3",
    "opp_fg3a",
    "opp_fg3_pct",
    "opp_fg2",
    "opp_fg2a",
    "opp_fg2_pct",
    "opp_ft",
    "opp_fta",
    "opp_ft_pct",
    "opp_orb",
    "opp_drb",
    "opp_trb",
    "opp_ast",
    "opp_stl",
    "opp_blk",
    "opp_tov",
    "opp_pf",
    "opp_pts"
]


def fetch_team_csv(team):
    resp = requests.get(URL.format(team))
    soup = bs4.BeautifulSoup(resp.text, "html5lib")
    table = soup.table
    seasons = {}
    for tr in table.tbody.find_all("tr"):
        if 'class' in tr.attrs:
            if 'thead' in tr['class']:
                continue
        year = tr.th.string
        year0 = int(year.split("-")[0])
        if year0 < 1973 or year0 > 2016:
            continue
        seasons[year] = season = {}
        for td in tr.find_all("td"):
            stat_field = td["data-stat"]
            if stat_field in STATS:
                if stat_field in STR_FIELDS:
                    stat = str(td.string)
                else:
                    if td.string is None:
                        stat = np.nan
                    else:
                        stat = float(td.string)
                season[stat_field] = stat

    resp = requests.get(URL.format(team) + "stats_basic_totals.html")
    soup = bs4.BeautifulSoup(resp.text, "html5lib")
    table = soup.table

    for tr in table.tbody.find_all("tr"):
        if 'class' in tr.attrs:
            if 'thead' in tr['class']:
                continue
        year = tr.th.string
        year0 = int(year.split("-")[0])
        if year0 < 1973 or year0 > 2016:
            continue
        season = seasons[year]
        for td in tr.find_all("td"):
            stat_field = td["data-stat"]
            if stat_field in STATS:
                if stat_field in STR_FIELDS:
                    stat = str(td.string)
                else:
                    if td.string is None:
                        stat = np.nan
                    else:
                        stat = float(td.string)
                season[stat_field] = stat

    resp = requests.get(URL.format(team) + "opp_stats_basic_totals.html")
    soup = bs4.BeautifulSoup(resp.text, "html5lib")
    table = soup.table

    for tr in table.tbody.find_all("tr"):
        if 'class' in tr.attrs:
            if 'thead' in tr['class']:
                continue
        year = tr.th.string
        year0 = int(year.split("-")[0])
        if year0 < 1973 or year0 > 2016:
            continue
        season = seasons[year]
        for td in tr.find_all("td"):
            stat_field = td["data-stat"]
            # and (stat_field not in OPP_FIELDS_SKIP):
            # print(stat_field, stat_field in STATS,
            #       not stat_field in OPP_FIELDS_SKIP)
            if (stat_field in STATS) and not (stat_field in OPP_FIELDS_SKIP):
                if stat_field in STR_FIELDS:
                    stat = str(td.string)
                else:
                    if td.string is None:
                        stat = np.nan
                    else:
                        stat = float(td.string)
                season[stat_field] = stat

    df = pd.DataFrame.from_dict(seasons, orient='index').reset_index()
    df['year'] = df['index']
    del df['index']
    df["team"] = team
    # df['games'] = df['wins'] + df['losses']
    # df['win_pct'] = df['wins'] / df['games']
    # df['win_logratio'] = np.log(df['wins'] / df['losses'])

    # df['net_rtg'] = df['off_rtg'] - df['def_rtg']
    # df['rtg_logratio'] = np.log(df['off_rtg'] / df['def_rtg'])

    return df


frames = []
for team in TEAMS:
    print(team)
    frames.append(fetch_team_csv(team))
    time.sleep(.5)

df = pd.concat(frames).sort_values('year')

df.to_csv("team_season_data.csv")
