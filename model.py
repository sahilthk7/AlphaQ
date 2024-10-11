import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump

# Load the dataset
df = pd.read_csv('restaurant_staff_schedule.csv')

# Features and target variables
X = df[['restaurant_id', 'avg_traffic', 'workload', 'burnout']].values
y = df[['employee_satisfaction']].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# MLP Regressor model
mlp = MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', solver='adam', max_iter=1000, early_stopping=True)
mlp.fit(X_train_scaled, y_train)

# Model evaluation
y_pred = mlp.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Save the model and scaler
dump(mlp, 'mlp_model.joblib')
dump(scaler, 'scaler.joblib')
