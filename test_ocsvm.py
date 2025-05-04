# test_ocsvm.py

import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import MinMaxScaler
from joblib import load
from tqdm.auto import tqdm
import glob
import os

import re

def numeric_sort_key(filename):
    match = re.search(r'model(\d+)_', filename)
    return int(match.group(1)) if match else float('inf')

init_flag = 0

# Parameters
np.random.seed(0)

# Load dataset
df = pd.read_csv("IndirectBP/stats_vips_IndirectBP_16/Data-traffic-distribution.csv")
class_column = 'Applications (Label Classes)'
df[class_column], label_mapping = pd.factorize(df[class_column], sort=True)
labels = label_mapping

output = []
tmp_out = []
tmp_out.append(['Features: 16', '', '', '', '', '', '', '', ''])

model_files = [f for f in sorted(os.listdir("Golden/stats_vips_16/saved_models"), key=numeric_sort_key) if f.endswith('.joblib')]

for model_file in tqdm(model_files):
    print(f"Testing model: {model_file}")

    # Parse filename parts
    parts = model_file.split('_')
    target_class_name = parts[2]
    
    # Parse nu, gamma, and noise percentage
    nu_part = model_file.split('_nu')[1]
    nu = nu_part.split('_gamma')[0]
    gamma_part = nu_part.split('_gamma')[1]
    gamma = gamma_part.split('_upsampling')[0]
    percentage_part = gamma_part.split('noise')[-1].replace('.joblib', '')
    noise_percentage = int(percentage_part)

    print(f"Testing model for Target Class: {target_class_name}, Nu: {nu}, Gamma: {gamma}")

    # Find index of target class
    try:
        index = np.where(labels == target_class_name)[0][0]
    except IndexError:
        print(f"Class {target_class_name} not found in data!")
        continue

    # Prepare data
    X_outlier = df[df[class_column] == index].to_numpy()[:, :16]

    scaler = MinMaxScaler()
    X_outlier = scaler.fit_transform(X_outlier)

    model_path = os.path.join("Golden/stats_vips_16/saved_models", model_file)
    clf = load(model_path)

    # Only test on outliers
    y_pred_outlier = clf.predict(X_outlier)

    TN = (y_pred_outlier == -1).sum()
    FP = (y_pred_outlier == 1).sum()

    # No TP/FN since we aren't testing inliers
    TP = 0
    FN = 0

    accuracy = (TN) / (TN + FP) * 100 if (TN + FP) > 0 else 0
    if(init_flag == 0):
        tmp_out.append([f'Target Class: {target_class_name}', 'TP', 'FN', 'FP', 'TN', 'ACC (%)', 'Noise Percentage', 'Upsampling', ''])
        init_flag = 1
    
    tmp_out.append([f'Nu: {nu}, Gamma: {gamma}', TP, FN, FP, TN, accuracy, noise_percentage, '40', ''])

output.append(tmp_out)
output = np.concatenate(output, axis=1)
out = pd.DataFrame(output)
out.to_csv("IndirectBP/stats_vips_IndirectBP_16/Testing-Results.csv", header=False, index=False, mode='a')
