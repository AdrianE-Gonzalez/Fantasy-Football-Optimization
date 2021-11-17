import Load_Dataset as ld
import Linear_Regression as lr
import lineargraph as lg
import LassoLarsCV as lr2

# Call Machine Learning Code
# dataset, le_labels= ld.get_data()
train_data, train_le_labels= ld.Train_Dataset()
test_data, test_le_labels= ld.Test_Dataset()
print('')

# r_sq, x, slope, intercept= lr.create_model(train_data,test_data,test_le_labels)
# lg.run_graphs(r_sq,x,slope,intercept,'Linear_Regression')

r_sq, x, slope, intercept= lr2.create_model(train_data,test_data,test_le_labels)
lg.run_graphs(r_sq,x,slope,intercept,'LassoLarsCV')
