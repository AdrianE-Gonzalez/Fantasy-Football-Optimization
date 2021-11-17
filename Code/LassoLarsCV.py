# Add Imports
from sklearn.linear_model import LassoLarsCV
from sklearn.preprocessing import LabelEncoder
import numpy as np
import csv

# Create Model
def create_model(train_dataset, test_dataset,test_le_labels):
    print(train_dataset)
    print(test_dataset)
    # Split Dataset Into Training And Testing
    train=train_dataset.sample(frac=0.8,random_state=200) #random state is a seed value
    test=train_dataset.drop(train.index)
    
    # Split X And Y Values
    # Y Is Set To The Fantasy Points Column
    # X Is Set To Everything Else
    y_train= train_dataset['Actual']
    X_train= train_dataset.drop('Actual',axis=1)
    
    # y_test= test['Actual']
    # X_test= test.drop('Actual',axis=1)

    # Create Model
    model = LassoLarsCV(normalize=True)
    
    x_test_data = test_dataset

    model.fit(X_train,y_train)

    # predictions = model.predict(x_test)  # Gets a list of all predictions
    # Model Score
    r_sq = model.score(X_train, y_train)
    slope = model.coef_
    intercept = model.intercept_

    print('coefficient of determination:', r_sq)
    print('intercept:', intercept)
    print('slope:', slope)
    # Predict
    y_pred = model.predict(x_test_data)
    print('predicted response:', y_pred, sep='\n')

    # Used To Decode Label Encoder Based On Columns Encoded
    for xs in test_le_labels:
        encoder = LabelEncoder()
        encoder.classes_ = np.load('Dataset/Encoder/classes_test_'+str(xs)+'.npy',allow_pickle=True)
        test_dataset[xs] = encoder.inverse_transform(test_dataset[xs])

    with open('Projected_Season_LassoLarsCV.csv', mode='w') as flex:
        writer = csv.writer(flex, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator = '\n')

        for x in range(len(y_pred)):
            writer.writerow([test_dataset.iloc[x,0],y_pred[x]])

    return r_sq, X_train,slope, intercept