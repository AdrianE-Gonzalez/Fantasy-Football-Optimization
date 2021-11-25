from numpy.lib.function_base import append
import requests
from bs4 import BeautifulSoup
import re
import csv
import re

import pandas as pd
import numpy as np

def get_active_player_career(year_num):
    rootURL = 'https://www.pro-football-reference.com/'
    playerURL_list = []
    player_list = []

    ppr = 0
    ppf = 0.5


    # HTML cleaner
    def _strip_html(text):
        tag_re = re.compile(r'<[^>]+>')
        return tag_re.sub('', str(text))

    # URL Can Be Changed To Any Year
    url = 'https://www.pro-football-reference.com/years/'+str(year_num)+'/scrimmage.htm'

    ## Scrape for RB stats
    res = requests.get(url)
    soup = BeautifulSoup(res.text,features="html.parser")

    # Parsed Used To Get Players From Active Year
    parsed = soup.findAll(
        'table', {
            'id': 'receiving_and_rushing'
        }
    )

    # Gets All The Rows From The Parsed Data
    rows = parsed[0].findAll('td')
    column_len = 30

    grouped_rows = [
        rows[i:i+column_len] for i in range(0, len(rows), column_len)
    ]

    # Gets The Player URL To Get Player Stats
    for i in grouped_rows:
        fullSTR = str(i)
        trimmed = re.search('href="(.*).htm">',fullSTR)
        playerURL = trimmed.group(1)
        playerURL = rootURL + playerURL + '.htm'
        playerURL_list.append(playerURL)

    # Sorts And Strips The html Code Onto A List
    table = [map(lambda x: _strip_html(x), row) for row in grouped_rows]

    # list Function Helps Get The Data From The Table
    for i in table:
        player_list.append(list(i))

    # Turns The List Of Players Into A DataFrame
    player_list = pd.DataFrame(player_list)

    # Gets Player Individual Career Stats From Year To Year
    def player_fetch(z,name):
        url = playerURL_list[z]
        print(url)
        player_career = []
        num_rows = 0
        pos = ''
        res = requests.get(url)
        soup = BeautifulSoup(res.text, features="html.parser")
        
        # Gets Player Position Based On HTML Paragraph
        # I Scrapped This Because, Not All Players Are Assigned A Position In The Website
        # content_ = soup.find_all('p')[1]
        # pos=''#str(content_.contents[2])[2:4] if str(content_.contents[2])[2:4]  else ''
        # print(pos)

        # Parsed Checks For Rushing and Receiving Tables, Else Checks For Receiving and Rushing Tables Else Makes Parsed A String
        parsed = (soup.findAll(
            'table', {
                'id': 'rushing_and_receiving'
            }
        )) if (soup.findAll(
            'table', {
                'id': 'rushing_and_receiving'
            }
        )) else (soup.findAll(
                        'table', {
                            'id': 'receiving_and_rushing'
                        }
        )) if (soup.findAll(
                        'table', {
                            'id': 'receiving_and_rushing'
                        }
        )) else ''
        
        # If There's No Data, Returns Empty Lists
        if parsed == '' :
            return [],[]

        print(name)
        # Gets The Rows Of The Table
        rows = parsed[0].findAll('tbody')
        rows= (rows[0].findAll('td'))
        num_rows = len(rows)/31

        # Gets The Labels From The Table
        labels_ = parsed[0].findAll('thead')
        labels_ = labels_[0].findAll('th')
        labels_names=[]

        # Initialized Variables
        grouped_rows = []
        col_len=0
        temp= []
        gnt=0

        # Stores Labels
        for x in labels_:
            labels_names.append(x)

        # Strips Labels HTML Code
        table_labels_ = [map(lambda x: _strip_html(x), row) for row in labels_]
        table_labels = []

        # Obtains The String Value From The tabel_labels_
        for x in table_labels_:
            temp = list(x)
            temp =  temp[0] if len(temp)==1 else 'None'
            table_labels.append(temp)

        # Turns table_labels Into A DataFrame
        table_labels = pd.DataFrame(table_labels).transpose()
        
        # Keeps Track If Table Is Rushing/Recieving Or Recieving/Rushing
        rushing_recieving = []
        rushing_recieving.append(table_labels.iloc[0,2])
        rushing_recieving.append(table_labels.iloc[0,3])
        
        # Temp Variable; Created This Because I Used The Same Variable For Looping And Changing Data During The Foreach Loop
        tempo = table_labels

        # Drop Columns Before The Age Column
        # Year Column Isn't Stored Under tbody From The HTML Code
        for x in tempo.columns:
            if tempo.iloc[0,x] == 'Age' :
                break
            else:
                table_labels = table_labels.drop(columns=[x])

        # Gets The Length Of table_labels
        column_len = table_labels.shape[1]-1
        temp= []

        for i in rows:
            # If Statements Specifically Fixes Table Shifts
            # Did Multiple If Statements So It Would Be Legible

            # Else, Stores Each Data Upto The column_len; Then Starts A New Row In The Table
            if str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Contract dispute</td>':
                temp= temp[:-1]
                col_len-=1
            elif str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Violation of league substance abuse policy</td>':
                temp= temp[:-1]
                col_len-=1
            elif str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Retired</td>':
                temp= temp[:-1]
                col_len-=1
            elif str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Injured (broken ankle)</td>':
                temp= temp[:-1]
                col_len-=1
            elif str(i)=='<td class="center" colspan="30" data-stat="reason">Missed season - Injured (ankle)</td>':
                temp= temp[:-1]
                col_len-=1
            else:
                temp.append(str(i))
                if col_len == column_len:
                    grouped_rows.append(temp)
                    col_len=0
                    temp= []
                else:
                    col_len+=1
        
        # Strips HTML Code
        table = [map(lambda x: _strip_html(x), row) for row in grouped_rows]
            
        player_career = []
        num_teams=31
        cnt = 0

        # Obtains Data Values From Stripped HTML Code
        for i in table:
            season_row = list(i)
            
            if(cnt < (num_rows - num_teams)):

                if(season_row[1] == 'Missed season - Contract dispute'):
                    season_row = season_row[2:]
            player_career.append(season_row)
            cnt+=1

        # Converts player_career Into A DataFrame
        player_career = pd.DataFrame(player_career)
        player_career.insert(loc=0, column='Player', value=name)
        print(player_career)

        return player_career, table_labels


    z = 0
    temp_name = player_list.iloc[0,0].replace("*","")
    table, labels = player_fetch(0,temp_name)
    labels= labels.values.tolist()[0]

    # Gather training data
    with open('train_'+str(year_num)+'.csv',mode='w') as train:
        writer = csv.writer(train, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(labels)

    for i in range(len(player_list)):
        name = player_list.iloc[i,0].replace("*","")

        # Obtains The Player's Career Table, And The Table Labels
        table, labels = player_fetch(z,name)
        
        # Checks If Table Isn't Empty
        # If The Length Is Equal 0, Then Its Considered False.
        if len(table):
            table.to_csv('train_'+str(year_num)+'.csv', mode='a', header=False, index=False)

        z=z+1
