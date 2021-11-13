import requests
from bs4 import BeautifulSoup
import re
import csv
import re

import pandas as pd
import numpy as np
rootURL = 'https://www.pro-football-reference.com/'
playerURL_list = []
player_list = []

ppr = 0
ppf = 0.5


# HTML cleaner
def _strip_html(text):
    tag_re = re.compile(r'<[^>]+>')
    return tag_re.sub('', str(text))

url = 'https://www.pro-football-reference.com/years/2019/scrimmage.htm'
## Scrape for RB stats
res = requests.get(url)
soup = BeautifulSoup(res.text,features="html.parser")

parsed = soup.findAll(
    'table', {
        'id': 'receiving_and_rushing'
    }
)

rows = parsed[0].findAll('td')

column_len = 30

grouped_rows = [
    rows[i:i+column_len] for i in range(0, len(rows), column_len)
]


for i in grouped_rows:
    fullSTR = str(i)
    trimmed = re.search('href="(.*).htm">',fullSTR)
    playerURL = trimmed.group(1)
    playerURL = rootURL + playerURL + '.htm'
    playerURL_list.append(playerURL)

table = [map(lambda x: _strip_html(x), row) for row in grouped_rows]

for i in table:
    player_list.append(list(i))

player_list = pd.DataFrame(player_list)

def player_fetch(z,name):
    url = playerURL_list[z]
    print(url)
    player_career = []
    num_rows = 0
    pos = ''
    res = requests.get(url)
    soup = BeautifulSoup(res.text, features="html.parser")
    
    content_ = soup.find_all('p')[1]
    pos=str(content_.contents[2])[2:4]
    print(pos)
    parsed = (soup.findAll(
        'table', {
            'id': 'rushing_and_receiving'
        }
    )) if (pos=='RB') else ( soup.findAll(
                'table', {
                    'id': 'passing'
                }
            )) if (pos=='QB') else (soup.findAll(
                    'table', {
                        'id': 'receiving_and_rushing'
                    }
    ))
        
        
        
    print(name)
    rows = parsed[0].findAll('tbody')
    rows= (rows[0].findAll('td'))
    num_rows = len(rows)/31

    column_len = 31
    grouped_rows = []
    col_len=0
    temp= []
    gnt=0
    for i in rows:

        if str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Contract dispute</td>':
            temp= temp[:-1]
            col_len-=1
        if str(i)!='<td class="center" colspan="30" data-stat="reason">Missed season - Contract dispute</td>':
            if pos=='QB':
                continue
            else:
                temp.append(str(i))
                if col_len == 30:
                    grouped_rows.append(temp)
                    col_len=0
                    temp= []
                else:
                    col_len+=1

    table = [map(lambda x: _strip_html(x), row) for row in grouped_rows]
       
    player_career = []
    num_teams=31
    cnt = 0

    for i in table:
        season_row = list(i)
        
        if(cnt < (num_rows - num_teams)):

            if(season_row[1] == 'Missed season - Contract dispute'):
                season_row = season_row[2:]
        player_career.append(season_row)
        cnt+=1

    player_career = pd.DataFrame(player_career)
    print(player_career)

    return player_career, pos


z = 0
# Gather training data
with open('train.csv',mode='w') as train:
    writer = csv.writer(train, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    labels = ['Player','Actual','Scrim yds','TOT TD','Fmbl','Rec','Tgt','Att','Age','Rush yds','Rec yds','Yds/rec','Rec TD','Rec 1D','Catch %','Rushing TD','Rush 1D','Rush long','Rec long','Yards/att','Touch','Yards/touch','Scrim yds','TOT TD','Fmbl','Rec','Tgt','Att','Age','Rush yds','Rec yds','Yds/rec','Rec TD','Rec 1D','Catch %','Rushing TD','Rush 1D','Rush long','Rec long','Yards/att','Touch','Yards/touch']
    writer.writerow(labels)

    for i in range(len(player_list)):
        name = player_list.iloc[i,0].replace("*","")
        table, pos = player_fetch(z,name)
        z=z+1
