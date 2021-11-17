import requests
from bs4 import BeautifulSoup
import re
import csv
import re
import pandas as pd
import matplotlib.pyplot as plt

def run_graphs(r_sq,x,slope, intercept, text_file):
    rootURL = 'https://www.pro-football-reference.com/'
    playerURL_list = []
    player_list = []

    ppr = 0
    ppf = 0.5

    # HTML cleaner
    def _strip_html(text):
        tag_re = re.compile(r'<[^>]+>')
        return tag_re.sub('', str(text))

    url = 'https://www.pro-football-reference.com/years/2018/scrimmage.htm'
    
    # Scrape for RB stats
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

    table = [map(lambda x: _strip_html(x), row) for row in grouped_rows]

    for i in table:
        player_list.append(list(i))

    # Save Projected Plus Actual Fantasy Points For The 2018 Season
    with open('Projected_Season_'+text_file+'.csv',mode='r') as flex:
        data = []
        reader = csv.reader(flex, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
        with open('2018.csv',mode='w') as evaluate:
            writer = csv.writer(evaluate,delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')
            for row in reader:
                name = row[0]
                proj = row[1]
                for i in player_list:
                    data = []
                    if('*' in i[0]):
                        i[0] = i[0][:-1]
                    if(i[0] == name):
                        data.append(name)
                        data.append(proj)
                        actual = int(i[27])/10 + int(i[28])*6 - 2*int(i[29]) + (ppr * int(i[7])) + ((int(i[11]) + int(i[20]))*ppf)
                        difference = actual - float(proj)
                        
                        percent_difference = ((difference) / ((actual+float(proj))/2)) *100
                        percent_difference = round(percent_difference, 2)
                        #percent_difference = str(percent_difference)+'%'
                        
                        data.append(actual)
                        data.append(difference)
                        data.append(percent_difference)
                        writer.writerow(data)

    dataset = pd.read_csv("2018.csv", sep=",",names=['Names', 'Projected','Actual', 'Difference','Percent Difference'], header=None)

    dataset= pd.DataFrame(dataset)
    print(dataset)

    y = intercept + slope * x

    # Graphs
    plt.scatter(dataset.iloc[:,2], dataset.iloc[:,1], color ='b')

    for i,txt in enumerate(dataset.iloc[:,0]):
        plt.annotate(txt, (dataset.iloc[:,2][i], dataset.iloc[:,1][i]))

    plt.xlabel('Actual')
    plt.ylabel('Projected')
    plt.show()                    