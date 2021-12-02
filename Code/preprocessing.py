from numpy.core.numeric import Inf
from numpy.lib.index_tricks import AxisConcatenator
import pandas as pd
from sklearn import preprocessing
import Load_Dataset as ld
import os

def preprocess_data(year_num):
    dataset= ld.get_raw_data(year_num)

    # Drops Last Column
    # Not All PLayers Contains AV ('Approximate Value')
    dataset= dataset.drop('AV', axis=1)

    # When Loading Dataset, Empty Indexes Are Set To NaN
    # Replaced NaNs with 0s
    dataset= dataset.fillna(0)

    # Fixes Empty Player Ages
    zeroes_players=[]
    # Gets The List Of Names With The Age Column Contains 0.0
    # I Probably Did This Way Too Complex, But It Works :/
    for x in pd.unique(((dataset.loc[dataset['Age'] == 0.0]).values)[:,0]):

        # Gets The First Year The Player Started In The NFL
        min_year= dataset.loc[dataset['Player Name'] == x, 'Year'].min()
        # Gets The Players Age Based On Their First Year (min_year)
        Age= pd.unique(dataset.loc[(dataset['Year']==(min_year)) & (dataset['Player Name'] == x)]['Age'])

        # Gets All The 0.0 Values In Dataset Under The 'Age' Column
        player_zero=dataset.loc[(dataset['Age'] == 0.0) & (dataset['Player Name'] == x)] 
        # Calculates The Difference In Starting Year And Current Year
        diff_year= (player_zero['Year']) - int(min_year)
        # Calculates The Age Based On The Starting Age Year And The Difference In Starting Year And Current Year
        curr_Age= (diff_year)+ int(Age[0])

        player_zero['Age'] = curr_Age
        for i in player_zero.values.tolist():
            zeroes_players.append(i)
    
    # Players With Empty Ages Stored 
    zeroes_players= pd.DataFrame(zeroes_players)
    # Replaces Every Age 0.0 With Actual Age
    dataset.loc[dataset['Age'] == 0.0,'Age'] = list(zeroes_players[2])
    
    # Changes Percentages Into Floats
    percent_data= []
    for dat in (dataset['Ctch%']):
        if type(dat) == str:
            dat= dat.strip('%')
        dat= float(dat)
        percent_data.append(dat)
    dataset['Ctch%']= percent_data

    # Drops Year, Tm, Pos, No.
    dataset= dataset.drop(['Tm','Pos','No.'], axis=1)

    return dataset

# Creates Training And Testing Datasets
# Only Obtains Data For Any Player With 2+ Years Of Experience
# Its Only Dropping Rookies, Because There Is No NFL Data To Help Determine The Prediction Of A Rookie
def train_test(dataset,year_num):
    training = []
    testing=pd.DataFrame()
    finished_training_dataset=pd.DataFrame()
    finished_testing_dataset= pd.DataFrame()
    prev_data= pd.DataFrame()
    curr_data=pd.DataFrame()
    # Creates A List Of Players
    # Dataset Contains Multiple PLayer Names Of The Same Player
    player_list= pd.unique(dataset['Player Name'])
    
    # Loops Through Player Names In Order To Strip The Predicted Year From The Full Dataset
    for i in player_list:
        player_stats= dataset.loc[dataset['Player Name'] == i]

        if (len(player_stats.index)>=2):
            # Drops Current Year Stats From player_stats And Applies It To curr_year
            # Needs To Set copy(), SO You Don't Copy By Reference
            curr_year= player_stats.iloc[-1:,:].copy()
            player_temp= player_stats.copy()

            # Calculates The Mean Values For All Columns Of The Dataset
            for x in player_temp.drop(['Player Name','Year'], axis=1):
                 player_temp[x]=round(player_temp[x].mean(),2)

            # Stores Last Row Of player_temp Dataframe (Since All Rows Contain The Same Data)
            testing= pd.concat([testing, player_temp.iloc[-1:,:]])

            player_stats=  player_stats.iloc[:-1,:]
            prev_year= player_stats.iloc[-1:,:]
            training_temp= []

            # Gets All Player Stats Except Predicted Year
            prev_data= pd.concat([prev_data,player_stats])

            # Stores Predicted Year
            curr_data= pd.concat([curr_data,curr_year])
            
            # This Could Use Some Optimization, Will Clean Up This Portion Of The Code At A Later Time
            # Loops Through The player_stats Dataframe And Caculates The Mean Of All Columns With Numbers
            player_stats= player_stats.sort_values(by=['Year'], ascending=False)
            for ij in range(len(player_stats)):
                training_temp.append(list(player_stats.iloc[ij:,2:].mean().round(2)))

            training_temp= pd.DataFrame(training_temp)
            training_temp.insert(loc=0, column='Player Name', value=list(player_stats['Player Name'].values))
            # Adds Year To The Second Column Of The Table
            training_temp.insert(loc=1, column='Year', value=list(player_stats['Year'].values))
            training_temp= training_temp.values.tolist()
            for x in training_temp:
                training.append(x)

    training= pd.DataFrame(training)
    training.columns=player_stats.columns

    # Creating Training And Testing Datasets Into CSV
    training_dataset= training
    testing_dataset= training
    
    training_dataset.insert(1,'Actual',list(round((training_dataset['YScm'] * (1/10)) + (training_dataset['Fmb'] * (-2)) + (training_dataset['RRTD'] * 6) + (training_dataset['Rec'] * 0.5),2)))

    # Drop 'GS', 'Y/G', 'A/G, 'R/G', 'Y/G.1', 'Y/Tgt'
    training_dataset= training_dataset.drop(['Year','GS', 'Y/G', 'A/G', 'R/G', 'Y/G.1', 'Y/Tgt'], axis=1)
    for x in training_dataset.drop(['Player Name','Actual','G','Age', 'Lng', 'Y/A', 'Lng.1', 'Y/R', 'Ctch%', 'Y/Tch'], axis=1):
        training_dataset[x]=(training_dataset[x]/(training_dataset['G'])).round(2)

    prev_data= prev_data.drop(['Year','GS', 'Y/G', 'A/G', 'R/G', 'Y/G.1', 'Y/Tgt'], axis=1)
    for x in prev_data.drop(['Player Name','G','Age', 'Lng', 'Y/A', 'Lng.1', 'Y/R', 'Ctch%', 'Y/Tch'], axis=1):
        prev_data[x]=(prev_data[x]/(prev_data['G'])).round(2)

    testing= testing.drop(['Year','GS', 'Y/G', 'A/G', 'R/G', 'Y/G.1', 'Y/Tgt'], axis=1)
    for x in testing.drop(['Player Name','G','Age', 'Lng', 'Y/A', 'Lng.1', 'Y/R', 'Ctch%', 'Y/Tch'], axis=1):
        testing[x]=(testing[x]/(testing['G'])).round(2)
    
    curr_data= curr_data.drop(['Year','GS', 'Y/G', 'A/G', 'R/G', 'Y/G.1', 'Y/Tgt'], axis=1)
    for x in curr_data.drop(['Player Name','G','Age', 'Lng', 'Y/A', 'Lng.1', 'Y/R', 'Ctch%', 'Y/Tch'], axis=1):
        curr_data[x]=(curr_data[x]/(curr_data['G'])).round(2)

    # After Dividing By G (Games Played), Replaces Any NaNs And inf Values With 0s, Created After Dividing By 0
    training_dataset= training_dataset.replace(Inf,0)
    training_dataset= training_dataset.fillna(0)

    prev_data= prev_data.replace(Inf,0)
    prev_data= prev_data.fillna(0)

    testing= testing.replace(Inf,0)
    testing= testing.fillna(0)

    curr_data= curr_data.replace(Inf,0)
    curr_data= curr_data.fillna(0)

    # Stores Player Names In Finished Datasets
    finished_training_dataset= pd.concat([finished_training_dataset,prev_data['Player Name']])
    finished_training_dataset.columns= ['Player Name']
    finished_testing_dataset= pd.concat([finished_testing_dataset,curr_data['Player Name']])
    finished_testing_dataset.columns= ['Player Name']

    # Drop G (Games Played) And Player Name
    training_dataset= training_dataset.drop(['G','Player Name'], axis=1)
    prev_data= prev_data.drop(['G', 'Player Name'], axis=1)
    testing= testing.drop(['G','Player Name'], axis=1)
    curr_data= curr_data.drop(['G', 'Player Name'], axis=1)

    # Concatenates training_dataset And prev_data Side By Side
    # set_index Fixed The Issue Of Creating NaN Values Instead Of Concatenating Dataframes Side By Side
    finished_training_dataset= pd.concat([finished_training_dataset.set_index(training_dataset.index),training_dataset, prev_data.set_index(training_dataset.index)], axis=1)
    finished_testing_dataset= pd.concat([finished_testing_dataset.set_index(testing.index),testing, curr_data.set_index(testing.index)], axis=1)

    finished_training_dataset.to_csv('./Dataset/Training Datasets/training_dataset_'+str(year_num)+'.csv',index=False)
    finished_testing_dataset.to_csv('./Dataset/Testing Datasets/testing_dataset_'+str(year_num)+'.csv',index=False)
    # return train, test

year_nums=[2017,2018,2019,2020]

for year_num in year_nums:
    dataset= preprocess_data(year_num)
    train_test(dataset,year_num)

