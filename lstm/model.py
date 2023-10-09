import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

df = pd.read_csv("dataset.csv")
df = df.fillna(0.0)
df = df.reset_index(drop=True)

time = df['DATE']
max_temp = df['TMAX']
min_temp = df['TMIN']
wind_speed = df['WSF2']
precipitation = df['PRCP']

df = pd.concat([max_temp, min_temp, wind_speed, precipitation], axis=1)
df.index = time

print(df)
look_back = 7


# Define a custom function to normalize the df
def normalize_df(df):
    mean = df.mean()
    std = df.std()
    return (df - mean) / std, mean, std

# Define a custom function to inverse normalize the df
def inverse_normalize_df(df, mean, std):
    return df * std + mean

# Prepare sequences of input df and corresponding target values
X, y = [], []
for i in range(len(df) - look_back):
    X.append(df.iloc[i:i+look_back, :-1].values)
    y.append(df.iloc[i+look_back, -1])

X = np.array(X)
y = np.array(y)

# Split the dfset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize the input df and keep track of mean and std for inverse normalization
X_train_norm, mean_X, std_X = normalize_df(X_train)
X_test_norm = (X_test - mean_X) / std_X  # Use the same mean and std for test df

# Normalize the target values (y) and keep track of mean and std for inverse normalization
y_train_norm, mean_y, std_y = normalize_df(y_train)
y_test_norm = (y_test - mean_y) / std_y  # Use the same mean and std for test df

# Build the LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(look_back, X_train_norm.shape[-1]), activation='relu'))
# model.add(Dropout(0.2))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
history = model.fit(X_train_norm, y_train_norm, epochs=160, batch_size=64, validation_data=(X_test, y_test), verbose=2)

# Plot the training loss and validation loss over epochs
plt.figure(figsize=(12, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
# Use the trained LSTM model to make predictions on the test df

print(X_test_norm)
predicted_values_norm = model.predict(X_test_norm)

# Inverse normalize the predicted PRCP values
predicted_values = inverse_normalize_df(predicted_values_norm, mean_y, std_y)

# Inverse normalize the actual PRCP values
y_test = inverse_normalize_df(y_test_norm, mean_y, std_y)

dates = range(len(predicted_values))

# Plot the actual and predicted PRCP values on the same graph
plt.figure(figsize=(12, 6))
plt.plot(dates, y_test, label='Actual PRCP', marker='o')
plt.plot(dates, predicted_values, label='Predicted PRCP', linestyle='--', marker='x')
plt.xlabel('Date')
plt.ylabel('PRCP')
plt.title('Actual vs. Predicted PRCP')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# model.save("model2.h5")