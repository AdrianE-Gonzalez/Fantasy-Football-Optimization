import Load_Dataset as ld
import Linear_Regression as lr
import lineargraph as lg
import LassoLarsCV as lr2
import Web_Scrapper as ws
# Call Machine Learning Code
# dataset, le_labels= ld.get_data()

#ws.get_active_player_career(2020)

year_num=2018
train_data, train_le_labels= ld.Train_Dataset(year_num)
test_data, test_le_labels= ld.Test_Dataset(year_num)
print(train_data)

r_sq, x, slope, intercept= lr.create_model(train_data,test_data,test_le_labels)
lg.run_graphs(r_sq,x,slope,intercept,'Linear_Regression',False)

# r_sq, x, slope, intercept= lr2.create_model(train_data,test_data,test_le_labels)
# lg.run_graphs(r_sq,x,slope,intercept,'LassoLarsCV',True)
