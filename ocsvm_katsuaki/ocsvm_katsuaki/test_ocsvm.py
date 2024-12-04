import pandas as pd
import numpy as np

from sklearn import svm
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import load_iris  # Importing the dataset from scikit-learn

# Load the Iris dataset
iris = load_iris()

# Convert the dataset to a DataFrame for easier manipulation
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df['Species'] = iris.target  # Add the species (target) column

# Map target values to species names to match the previous code (0 = 'setosa', 1 = 'versicolor', 2 = 'virginica')
species_mapping = {0: 'Iris-setosa', 1: 'Iris-versicolor', 2: 'Iris-virginica'}
df['Species'] = df['Species'].map(species_mapping)

# Select data points where the 'Species' is 'Iris-virginica'
X_train = df[df['Species'] == "Iris-virginica"]

# Extract 'PetalLengthCm' and 'PetalWidthCm' columns for training (first 40 samples)
# In the scikit-learn dataset, feature names are slightly different:
X_train = X_train[['petal length (cm)', 'petal width (cm)']].values[:40, :]

# Rescale the data using MinMaxScaler, scaling each feature to a range between 0 and 1
X_train = MinMaxScaler().fit_transform(X_train)

# Uncomment the following line if you want to remove rows where all features are scaled to 1
# X_train = np.delete(X_train, (np.where(X_train == 1)), axis=0)

# Define a list of nu values (hyperparameter controlling the fraction of support vectors)
NUs = [0.1, 0.05, 0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00005, 0.00001]

# Define a list of gamma values (hyperparameter controlling the influence of each training sample)
GAMMAs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01, 0.005, 0.001]

# Loop through each combination of nu and gamma
for nu in NUs:
    for gamma in GAMMAs:
        # Initialize the One-Class SVM model with the current nu and gamma, using an RBF (Radial Basis Function) kernel
        clf = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
        
        # Fit the model on the training data (Iris-virginica samples)
        clf.fit(X_train)
        
        # Predict using the trained model on the same training data
        y_pred_train = clf.predict(X_train)
        
        # Count how many training samples are classified as outliers (predicted as -1)
        n_error_train = y_pred_train[y_pred_train == -1].size

        # If the number of errors (outliers) is 0 or 1, print the following:
        if n_error_train == 0 or 1:
            # Print the number of iterations it took for the model to converge
            print(clf.n_iter_)
            
            # Print the current nu, gamma, and the number of errors (outliers)
            print(nu, gamma, n_error_train)
            
            # Get the indices of the outliers (samples predicted as -1)
            error_index = np.where(y_pred_train == -1)[0]
            
            # Retrieve the outlier samples based on the indices
            error_train = X_train[error_index]
            
            # Print the indices and the outlier samples
            print(error_index, error_train)
