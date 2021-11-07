import Load_Dataset as ld
import Linear_Regression as lr

# Call Machine Learning Code
dataset, le_labels= ld.get_data()
print('')
lr.create_model(dataset, le_labels)