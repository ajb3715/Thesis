import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tqdm.auto import tqdm

# Random seed for reproducibility
np.random.seed(0)
tf.random.set_seed(0)

# Load Data
df = pd.read_csv("MRUCache/stats_x264_MRURP_16/Data-traffic-distribution-Comparison.csv")
class_column = 'Applications (Label Classes)'
df[class_column], label_mapping = pd.factorize(df[class_column], sort=True)
labels = label_mapping

# Normalize Data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(df.iloc[:, :-1])

def create_lstm_model(input_shape):
    model = Sequential([
        LSTM(32, return_sequences=True, input_shape=input_shape),
        LSTM(16, return_sequences=False),
        Dense(8, activation='relu')
    ])
    return model

# Prepare data for LSTM
sequence_length = 10  # Define sequence length
X_sequences, y_labels = [], []
for i in range(len(data_scaled) - sequence_length):
    X_sequences.append(data_scaled[i:i+sequence_length])
    y_labels.append(df[class_column].iloc[i+sequence_length])
X_sequences, y_labels = np.array(X_sequences), np.array(y_labels)

# Train LSTM to extract features
lstm_model = create_lstm_model((sequence_length, data_scaled.shape[1]))
lstm_features = lstm_model.predict(X_sequences)

# Train OC-SVM on LSTM features
clf = OneClassSVM(kernel='rbf', nu=0.1, gamma=0.01)
clf.fit(lstm_features)

# Predict anomalies
y_pred = clf.predict(lstm_features)
