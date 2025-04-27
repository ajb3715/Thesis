# train_ocsvm.py

import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import MinMaxScaler
from joblib import dump
from tqdm.auto import tqdm
import os

# Parameters
np.random.seed(0)
nums_samples = 40
percentages = [0, 10]
ratios = [0.9]
ratios_text = ['9-1']
NUs = [0.0001, 0.0002, 0.0003, 0.0004, 0.005, 0.05, 1./16., 0.1, 0.2, 0.5, 0.7, 0.9, 0.99]
GAMMAs = [0.0001, 0.0002, 0.0003, 0.0004, 0.005, 0.05, 1./16., 0.1, 0.2, 0.5, 0.7, 0.9, 0.99]

# Load dataset
df = pd.read_csv("DropCore/stats_streamcluster_drop10_16/Data-traffic-distribution-Comparison.csv")
class_column = 'Applications (Label Classes)'
df[class_column], label_mapping = pd.factorize(df[class_column], sort=True)
labels = label_mapping

# Make sure model save path exists
os.makedirs("DropCore/stats_streamcluster_drop10_16/saved_models", exist_ok=True)

for percentage in percentages:
    for ratio, ratio_text in zip(ratios, ratios_text):
        output = []
        tmp_out = []
        tmp_out.append(['Features: 16', '', '', '', '', '', '', '', ''])

        for index in tqdm(np.unique(df[class_column])):
            target_class_name = labels[index]
            print(f"Training Target Class: {target_class_name}")

            X_train = df[df[class_column] == index].to_numpy()[:, :16]
            np.random.shuffle(X_train)

            scaler = MinMaxScaler()
            X_train = scaler.fit_transform(X_train)

            split_index = int(X_train.shape[0] * ratio)
            X_train_target = X_train[:split_index, :]
            X_test_target = X_train[split_index:, :]

            # Data augmentation
            if percentage != 0:
                augmented_data = []
                for sample in X_train_target:
                    for _ in range(nums_samples):
                        noise = np.random.normal(0, (percentage/100)*np.abs(sample), size=sample.shape)
                        augmented_data.append(sample + noise)
                X_train_target = np.vstack((X_train_target, np.array(augmented_data)))

            tmp_out.append([f'Target Class: {target_class_name}', 'TP', 'FN', 'FP', 'TN', 'ACC (%)', 'Noise Percentage', 'Upsampling', ''])

            for nu in tqdm(NUs):
                for gamma in tqdm(GAMMAs):
                    clf = OneClassSVM(kernel='rbf', nu=nu, gamma=gamma)
                    clf.fit(X_train_target)

                    # Save model
                    model_filename = f"DropCore/stats_streamcluster_drop10_16/saved_models/upsamlping_noise{percentage}_ocsvm_{target_class_name}_nu{nu}_gamma{gamma}_upsamlping_noise{percentage}.joblib"
                    dump(clf, model_filename)

                    # Test on inliers only
                    y_pred_train = clf.predict(X_test_target)
                    FN = (y_pred_train == -1).sum()
                    TP = (y_pred_train == 1).sum()
                    FP = 0  # No testing on outliers here
                    TN = 0

                    accuracy = (TP + TN) / (TP + FP + FN + TN) * 100 if (TP+FP+FN+TN) > 0 else 0

                    tmp_out.append([f'Nu: {nu}, Gamma: {gamma}', TP, FN, FP, TN, accuracy, int(percentage), nums_samples, ''])

            tmp_out.append(['', '', '', '', '', '', '', '', ''])

        output.append(tmp_out)

        output = np.concatenate(output, axis=1)
        out = pd.DataFrame(output)
        out.to_csv("DropCore/stats_streamcluster_drop10_16/Training-Results.csv", header=False, index=False, mode='a')
