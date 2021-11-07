# Add Imports
from os import X_OK
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Create Model
def create_model(dataset, le_labels):
    # Split Dataset Into Training And Testing
    train=dataset.sample(frac=0.8,random_state=200) #random state is a seed value
    test=dataset.drop(train.index)

    # Split X And Y Values
    # Y Is Set To The Fantasy Points Column
    # X Is Set To Everything Else
    y_train= train['Total_DKP']
    X_train= train.drop('Total_DKP',axis=1)
    
    y_test= test['Total_DKP']
    X_test= test.drop('Total_DKP',axis=1)

    # Create Model
    model = LinearRegression()

    # Fit Model
    model.fit(X_train,y_train)

    # Model Score
    r_sq = model.score(X_test, y_test)
    print('coefficient of determination:', r_sq)
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)

    # Predict
    y_pred = model.predict(X_test)
    print('predicted response:', y_pred, sep='\n')

    # Used To Decode Label Encoder Based On Columns Encoded
    # for xs in le_labels:
    #     encoder = LabelEncoder()
    #     encoder.classes_ = np.load('Dataset/Encoder/classes_'+str(xs)+'.npy',allow_pickle=True)
    #     X_test[xs] = encoder.inverse_transform(X_test[xs])
