# Add Imports
from os import X_OK
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import LabelEncoder
import numpy as np
import matplotlib.pyplot as plt

# Create Model
def create_model(dataset,le_labels):
    print(dataset)
    # Split Dataset Into Training And Testing
    train=dataset.sample(frac=0.8,random_state=200) #random state is a seed value
    test=dataset.drop(train.index)

    # Split X And Y Values
    # Y Is Set To The Fantasy Points Column
    # X Is Set To Everything Else
    y_train= train['Actual']
    X_train= train.drop('Actual',axis=1)
    
    y_test= test['Actual']
    X_test= test.drop('Actual',axis=1)

    # Create Model
    model = LassoCV()

    # Fit Model
    model.fit(X_train,y_train)

    # Model Score
    r_sq = model.score(X_test, y_test)
    print('coefficient of determination:', r_sq)
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)

    # Predict
    y_pred = model.predict(X_test)
    # print('predicted response:', y_pred, sep='\n')
    plt.scatter(X_test, y_test, color ='b')
    plt.plot(X_test, y_pred, color ='k')
    
    plt.show()

    print(model.score(X_test, y_test))


    # # Used To Decode Label Encoder Based On Columns Encoded
    # for xs in le_labels:
    #     encoder = LabelEncoder()
    #     encoder.classes_ = np.load('Dataset/Encoder/classes_'+str(xs)+'.npy',allow_pickle=True)
    #     X_test[xs] = encoder.inverse_transform(X_test[xs])
    #     print(X_test[xs])
