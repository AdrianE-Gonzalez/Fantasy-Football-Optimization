from numpy.lib.function_base import append
import requests
from bs4 import BeautifulSoup
import re
import csv
import re

import pandas as pd
import numpy as np
import os 

# Gets All
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

        # Parsed Checks For Rushing and Receiving Tables, Else Checks For Receiving and Rushing Tables Else Makes Parsed A String Variable
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
        # Some Players Are Listed As Active, But Don't Have Any Rushing & Receiving Stats
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

        # Gets The Years
        # Used This In Order To Determine What Year To Drop Based On Year We Are Trying To Get
        #       Ex. If We Want 2018, We Make Sure To Drop Every Year After That; Only If The Player Has Stats After 2018
        year_ = parsed[0].findAll('tbody')
        year_= (year_[0].findAll('th'))

        # Initialized Variables
        grouped_rows = []
        col_len=0
        temp= []

        # Strips Labels HTML Code
        table_labels_ = [map(lambda x: _strip_html(x), row) for row in labels_]
        table_labels = []

        years_p = [map(lambda x: _strip_html(x), row) for row in year_]
        years_played_ = []

        # Obtains The String Value From The tabel_labels_
        for x in table_labels_:
            temp = list(x)
            temp =  temp[0] if len(temp)!=0 else 'None'
            table_labels.append(temp)

        # Obtains The String Value From The years_p
        # Added Another If Statement To temp Variable, Because Players Such As Amari Cooper Changed Teams In The Middle Of The Season, 
        # But Contains An * For The Year, Instead Of An Empty String; Which Just Means He Was Selected For The ProBowl That Year
        for x in years_p:
            temp = list(x)
            temp =  (temp[0] if str(temp[0])!='*' else years_played_[-1])if len(temp)!=0 else years_played_[-1]
            years_played_.append(temp)

        # Turns table_labels Into A DataFrame
        table_labels = pd.DataFrame(table_labels).transpose()
        
        # Keeps Track If Table Is Rushing/Receiving Or Receiving/Rushing
        # Used To Convert Receiving & Rushing Tables into Rushing & Receiving Table
        rushing_receiving = []
        rushing_receiving.append(table_labels.iloc[0,2])
        rushing_receiving.append(table_labels.iloc[0,3])
        
        # Temp Variable; Created This Because I Used The Same Variable For Looping And Changing Data During The Foreach Loop
        tempo = table_labels

        # Drops Columns Before The Age Column
        # Year Column Isn't Stored Under tbody From The HTML Code So We Dont Need That Label
        for x in tempo.columns:
            if tempo.iloc[0,x] == 'Age' :
                break
            else:
                table_labels = table_labels.drop(columns=[x])

        # Gets The Length Of table_labels
        # We Do this Because Some Players Doesn't Contain The AV Column
        column_len = table_labels.shape[1]-1
        temp= []

        for i in rows:
            # If Player Missed Season, Adds 0s To The Row
            # Else, Stores Each Data Upto The column_len; Then Starts A New Row In The Table
            if str(i).find('Missed season') > -1:
                temp= temp[:-1]
                zeroes= [0] * column_len
                grouped_rows.append(zeroes)
                col_len-=1
            else:
                temp.append(str(i))
                # If The col_len Is Equal To column_len, Then It Appends The Row Onto The grouped_rows And Resets col_len To 0
                # Else It Adds 1 To col_len
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
        temp_year=years_played_
        # Adds Player Name To The Beginning Of The Table
        player_career.insert(loc=0, column='Player', value=name)
        # Adds Year To The Second Column Of The Table
        player_career.insert(loc=1, column='Year', value=temp_year)

        # Checks If The Table Is Receiving & Rushing
        # Changes Stats Order From Receiving & Rushing To Rushing & Receiving
        if rushing_receiving[0]=='Receiving':
            Temp= pd.concat([player_career.iloc[:,:7],player_career.iloc[:,18:26],player_career.iloc[:,7:18],player_career.iloc[:,26:]], axis=1)
            player_career = Temp
        
        # Keeps Track Of The Year Its Currently Checking
        curr_year = years_played_[-1]
        
        # Loops Through The Years And Drops Any Year After The year_num
        # This Is Meant To Drop The Stats After The year_num That Current Active Players Are Still Playing In The NFL After The Year Num
        while str(curr_year) != str(year_num):
            player_career= player_career.iloc[:-1, :]
            years_played_= years_played_[:-1]
            curr_year=years_played_[-1]
        print(player_career)
        return player_career, table_labels


    z = 0
    temp_name = player_list.iloc[0,0].replace("*","")
    table, labels = player_fetch(0,temp_name)
    labels= labels.values.tolist()[0]
    labels.insert(0,'Player Name')
    labels.insert(1,'Year')

    # Gather training data
    with open('./Dataset/Raw Data/raw_data_'+str(year_num)+'.csv',mode='w') as train:
        writer = csv.writer(train, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(labels)

    for i in range(len(player_list)):
        name = player_list.iloc[i,0].replace("*","")

        # Obtains The Player's Career Table, And The Table Labels
        table, labels = player_fetch(z,name)
        
        # Checks If Table Isn't Empty
        # If The Length Is Equal 0, Then Its Considered False.
        if len(table):
            table.to_csv('./Dataset/Raw Data/raw_data_'+str(year_num)+'.csv', mode='a', header=False, index=False)

        z=z+1

# You Only Need To Do This Once, Unless You Want To Get The Upcoming Season
# get_active_player_career(2017)
# get_active_player_career(2018)
# get_active_player_career(2019)
# get_active_player_career(2020)
# get_active_player_career(2021)