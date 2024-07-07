import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Load the dataset
file_path = r'C:\Users\syedk\OneDrive\Desktop\Slash Mark IT Startup\Basic Project - 2 (XGBoost Home Price Prediction)\kc_house_data.csv'
data = pd.read_csv(file_path)

# Drop columns that won't be used for the prediction
data = data.drop(columns=['id', 'date'])

# Handle missing values (if any)
data = data.dropna()

# Define the features (X) and the target (y)
X = data.drop(columns=['price'])
y = data['price']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Linear Regression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Predict on the training set
y_train_pred_lr = lr_model.predict(X_train)

# Calculate residuals
residuals = y_train - y_train_pred_lr

# Initialize the XGBoost model
xgb_model = xgb.XGBRegressor(objective='reg:squarederror')

# Define the parameter grid for grid search
param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.05, 0.1, 0.2],
    'max_depth': [4, 6, 8],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}

# Perform grid search with cross-validation on the residuals
grid_search = GridSearchCV(estimator=xgb_model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1)
grid_search.fit(X_train, residuals)

# Get the best model from grid search
best_xgb_model = grid_search.best_estimator_

# Predict on the test set with Linear Regression
y_test_pred_lr = lr_model.predict(X_test)

# Predict on the test set with Gradient Boosting
residuals_test_pred = best_xgb_model.predict(X_test)

# Combine the predictions
y_test_pred_combined = y_test_pred_lr + residuals_test_pred

# Evaluate the combined model's performance
mae_combined = mean_absolute_error(y_test, y_test_pred_combined)
mse_combined = mean_squared_error(y_test, y_test_pred_combined)
rmse_combined = mean_squared_error(y_test, y_test_pred_combined, squared=False)
r2_combined = r2_score(y_test, y_test_pred_combined)

print(f"Combined Model Mean Absolute Error (MAE): {mae_combined}")
print(f"Combined Model Mean Squared Error (MSE): {mse_combined}")
print(f"Combined Model Root Mean Squared Error (RMSE): {rmse_combined}")
print(f"Combined Model R^2 Score: {r2_combined}")

# Save the models
joblib.dump(lr_model, 'linear_regression_model.pkl')
best_xgb_model.save_model('xgboost_best_model.json')
