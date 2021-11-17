# Add Imports
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
# Label Encoder Is Used To Convert Strings To Integers
# EX. The String "QB" Is Set To Integer 15

# Currently Used Dataset
def Train_Dataset():
    train_data = pd.read_csv("train.csv", sep=",")

    # Initialize List To Store Columns Encoded
    train_le_labels= []

    # Loops Through Dataframe Columns And Apply Label Encoder Onto Any Columns With Strings Indexes
    for z in train_data.columns:
        if type(train_data.loc[0,z]) == str:
            le = LabelEncoder()
            train_data[z] = le.fit_transform(train_data[z])
            train_le_labels.append(z)

            # Saved Label Encoder For Later Use (To Decode Any Integer To It's Original String)
            np.save('Dataset/Encoder/classes_'+'train_'+str(z)+'.npy', le.classes_)
    print('')

    return train_data, train_le_labels
    
def Test_Dataset():
    test_data = pd.read_csv("test.csv", sep=",")

    # Initialize List To Store Columns Encoded
    test_le_labels= []

    # Loops Through Dataframe Columns And Apply Label Encoder Onto Any Columns With Strings Indexes
    for z in test_data.columns:
        if type(test_data.loc[0,z]) == str:
            le = LabelEncoder()
            test_data[z] = le.fit_transform(test_data[z])
            test_le_labels.append(z)

            # Saved Label Encoder For Later Use (To Decode Any Integer To It's Original String)
            np.save('Dataset/Encoder/classes_'+'test_'+str(z)+'.npy', le.classes_)
    print('')

    return test_data, test_le_labels

# Different Dataset That Was Used For Testing Algorithms
# Returns Dataset And List Of Columns Encoded
def get_data():
    # Grab Dataset And Store It Onto A Pandas Dataframe
    file_path= './Dataset/nfl_pass_rush_receive_raw_data_2020_season.csv'
    # Add Load Data Set
    dataset= pd.read_csv(file_path)

    # Dropped Any Columns That Are Irrelevant To Our Project Goals
    dataset= dataset.drop(['game_id','player_id','OT','Off_DKP','Total_FDP','Off_FDP','Total_SDP','Off_SDP'], axis=1)

    # Initialize List To Store Columns Encoded
    le_labels= []

    # Loops Through Dataframe Columns And Apply Label Encoder Onto Any Columns With Strings Indexes
    for z in dataset.columns:
        if type(dataset.loc[0,z]) == str:
            le = LabelEncoder()
            dataset[z] = le.fit_transform(dataset[z])
            le_labels.append(z)

            # Saved Label Encoder For Later Use (To Decode Any Integer To It's Original String)
            np.save('Dataset/Encoder/classes_'+str(z)+'.npy', le.classes_)

        # print(str(z)+' == ' + str(dataset.loc[0,z]))
    print('')

    # for xs in le_labels:
    #     encoder = LabelEncoder()
    #     encoder.classes_ = np.load('classes_'+str(xs)+'.npy',allow_pickle=True)
    #     dataset[xs] = encoder.inverse_transform(dataset[xs])
    #     # print(str(xs)+' == ' + str(dataset.loc[0,xs]))    
    
    return dataset, le_labels

Test_Dataset()



# 6pts per rushing td
# 4pts per passing td
# 1pt per 25 yrds passing
# 1pt per 10 yrds rushing
# -2pts per Int
# -2pts per Fumble Lost