import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, balanced_accuracy_score

# Load training and testing results
training_df = pd.read_csv("Golden/stats_vips_16/Training-Results.csv", header=None)
testing_df = pd.read_csv("IndirectBP/stats_vips_IndirectBP_16/Testing-Results.csv", header=None)

# Drop header rows that don’t contain metrics
training_df = training_df[training_df[0].str.contains("Nu:", na=False)].reset_index(drop=True)
testing_df = testing_df[testing_df[0].str.contains("Nu:", na=False)].reset_index(drop=True)

# Helper to parse parameter string
def parse_params(row):
    try:
        parts = row.split(", ")
        nu = float(parts[0].split(": ")[1])
        gamma = float(parts[1].split(": ")[1])
        return nu, gamma
    except Exception:
        return None, None

# Build combined rows
combined_rows = []

for i in range(len(training_df)):
    train_row = training_df.iloc[i]
    test_row = testing_df.iloc[i]

    train_nu, train_gamma = parse_params(train_row[0])
    test_nu, test_gamma = parse_params(test_row[0])



    # Sanity check (optional)
    assert np.isclose(train_nu, test_nu), f"nu mismatch at row {i}"
    assert np.isclose(train_gamma, test_gamma), f"gamma mismatch at row {i}"

    TP = int(train_row[1])
    FN = int(train_row[2])
    FP = int(test_row[3])
    TN = int(test_row[4])
    noise = int(test_row[6])
    upsampling = int(test_row[7])

    # Metrics
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    total = TP + FN + FP + TN
    accuracy = (TP + TN) / total if total > 0 else 0
    balanced_accuracy = (recall + specificity) / 2

    combined_rows.append([
        train_nu, train_gamma, noise, upsampling,
        TP, FN, FP, TN,
        precision, recall, specificity, f1,
        accuracy, balanced_accuracy
    ])

# Create output DataFrame
combined_df = pd.DataFrame(combined_rows, columns=[
    'nu', 'gamma', 'noise_percentage', 'upsampling',
    'TP', 'FN', 'FP', 'TN',
    'Precision', 'Recall', 'Specificity', 'F1-Score',
    'Accuracy', 'Balanced Accuracy'
])

# Save to CSV
combined_df.to_csv("IndirectBP/stats_vips_IndirectBP_16/Combined-OCSVM-Results.csv", index=False)
print("Saved combined results to Combined-OCSVM-Results.csv")
