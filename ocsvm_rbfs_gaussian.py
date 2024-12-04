# Import necessary libraries
import pandas as pd  # Data manipulation
import numpy as np  # Numerical operations and random generation
import matplotlib.pyplot as plt  # For plotting, though not used in this code
from sklearn.svm import OneClassSVM  # One-Class Support Vector Machine (SVM) for anomaly detection

# Random seed for reproducibility
np.random.seed(0)

# Parameters
# n_training_samples = 16  # Number of training samples (unused in this code)
# nums_features = [1, 4, 8, 16]  # List of feature counts to iterate over
nums_samples = 40  # List of sample sizes to iterate over
percentages = [0, 10, 20, 30, 40, 50]  # Different percentages of Gaussian noise
ratios = [0.9] # ratios = [0.8, 0.9]  # Data split ratios for train/test (80-20% or 90-10%)
ratios_text = ['9-1']# ratios_text = ['8-2', '9-1']  # Text labels for the split ratios
# List of different `nu` (a hyperparameter of OneClassSVM, controlling support vectors)
NUs = [0.00005, 0.00006, 0.00007, 0.00008, 0.00009, 0.0001, 0.0002, 0.0003, 0.0004, 0.005, 0.05, 1./16., 0.1, 0.2, 0.5, 0.7, 0.9, 0.99]
# List of different `gamma` values (another hyperparameter controlling kernel width in SVM)
GAMMAs = [0.00001, 0.00002, 0.00003, 0.00004, 0.00005, 0.00006, 0.00007, 0.00008, 0.00009, 0.0001, 0.0002, 0.0003, 0.0004, 0.005, 0.05, 1./16., 0.1, 0.2, 0.5, 0.7, 0.9, 0.99]

# Iterate through different configurations
for percentage in percentages:
    for ratio, ratio_text in zip(ratios, ratios_text):  # Iterate over train-test split ratios
        output = []  # Placeholder for storing results before writing to CSV
        # print(f'No. of features: {n_features}, No. of generated samples: {n_samples}, Split ratio: {ratio_text}, Gaussian percentage: {percentage}')
        
        # Read data from CSV based on current configuration (generated beforehand)
        df = pd.read_csv("HalfCache\stats_blackscholes_cachehalf_16/Data-traffic-distribution-Comparison.csv")
        
        # Column indicating the class labels
        class_column = 'Applications (Label Classes)'
        
        # Get unique class labels in the dataset
        labels = np.unique(df[class_column].to_numpy())
        
        # Convert class labels into numeric values (e.g., categorical to integer)
        df[class_column] = pd.factorize(df[class_column])[0]
        label_indices = np.unique(df[class_column].to_numpy())  # Get unique numeric labels
        
        tmp_out = []  # Temporary output for current configuration
        tmp_out.append(['Features: 16', '', '', '', '', '', '', '', ''])  # Formatting for CSV output

        # Iterate through each class (target class)
        for index in label_indices:
            print('Target class:', labels[index])
            
            # Select data points for the current class (target class) excluding the class label column
            X_train = df[df[class_column] == index].to_numpy()[:, :16]
            np.random.shuffle(X_train)  # Shuffle the rows to randomize

            # Split the data into training and testing based on the given ratio (80-20% or 90-10%)
            split_index = int(X_train.shape[0] * ratio)
            
            # Training data (target class)
            X_train_target = X_train[:split_index, :]

            # **Augment Training Data with Noise**
            if(percentage != 0):
                augmented_data = []
                for sample in X_train_target:
                    for _ in range(nums_samples):  # Generate `nums_samples` additional data points
                        noise = np.random.normal(0, (percentage / 100) * np.abs(sample), size=sample.shape)
                        augmented_data.append(sample + noise)
                
                # Convert augmented data to NumPy array and append to the original training data
                X_train_target_augmented = np.vstack((X_train_target, np.array(augmented_data)))
                    
            # Test data from the target class (benign cases)
            X_test_target = X_train[split_index:, :]
            
            # Test data from other classes (anomalous cases)
            X_test_others = df[df[class_column] != index].to_numpy()[:, :16]

            # Add target class header to the temporary output
            tmp_out.append([f'Target Class: {labels[index]}', 'TP', 'FP', 'FN', 'TN', 'ACC (%)', 'Noise Percantages', 'Upsampling', ''])  # TP, FP, etc. are placeholders for output

            # Iterate over `nu` and `gamma` hyperparameters of OneClassSVM
            for nu in NUs:
                for gamma in GAMMAs:
                    # Initialize OneClassSVM with current parameters
                    clf = OneClassSVM(kernel='rbf', nu=nu, gamma=gamma)
                    
                    clf.fit(X_train_target)  # Train the model on the target class

                    # Predict on test data from the same class (expected to be positive)
                    y_pred_train = clf.predict(X_test_target)
                    FP = y_pred_train[y_pred_train == -1].size  # False positives (misclassified as anomalies)
                    TN = y_pred_train[y_pred_train == 1].size  # True negatives (correctly classified as non-anomalous)

                    # Predict on data from other classes (expected to be anomalies)
                    y_pred_test = clf.predict(X_test_others)
                    TP = y_pred_test[y_pred_test == -1].size  # True positives (correctly classified as anomalies)
                    FN = y_pred_test[y_pred_test == 1].size  # False negatives (misclassified as benign)

                    # Calculate accuracy and store results in the temporary output
                    accuracy = (TP + TN) / (TP + FP + FN + TN) * 100
                    tmp_out.append([f'Nu: {nu}, Gamma: {gamma}', TP, FP, FN, TN, accuracy, int(percentage), nums_samples, ''])  # Append to CSV output

            tmp_out.append(['', '', '', '', '', '', '', '', ''])  # Add spacing in output between target classes

        output.append(tmp_out)

        # Combine all output rows for this configuration and save to CSV
        output = np.concatenate(output, axis=1)  # Merge results for different features
        out = pd.DataFrame(output)  # Convert to DataFrame for easier CSV export
        out.to_csv("HalfCache/stats_blackscholes_cachehalf_16/Data-traffic-distribution-Results.csv", header=False, index=False, mode='a')  # Save the result