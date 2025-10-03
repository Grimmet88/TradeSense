# File: machine_learning.py
# Description: Loads historical data, engineers features, trains a Random Forest Classifier,
# and evaluates its ability to predict the next day's price movement.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import numpy as np # Added for simulating sentiment data
import os

INPUT_FILE = "trade_data.pkl"
SENTIMENT_FILE = "sentiment_data.pkl" # New file path for external scraped data
N_DAYS = 5 # Number of previous days' features to use
TARGET_COL = 'Target'

def get_sentiment_data(index):
    """
    ATTENTION: This is a placeholder function to simulate external scraped data.
    In a real-world scenario, you would run a separate script to scrape news, 
    social media, etc., and save the final sentiment score per day to SENTIMENT_FILE.

    If SENTIMENT_FILE exists, load it. Otherwise, create synthetic data
    for the dates in the main financial data (index) to ensure the script runs.
    """
    if os.path.exists(SENTIMENT_FILE):
        print(f"-> Loading external sentiment data from {SENTIMENT_FILE}...")
        return pd.read_pickle(SENTIMENT_FILE)
    else:
        print(f"-> WARNING: Sentiment data not found. Generating synthetic sentiment for integration.")
        # Create synthetic sentiment data tied to the main data index
        # Random data centered around 0, representing daily sentiment score
        synthetic_sentiment = pd.Series(
            np.random.normal(loc=0.0, scale=0.5, size=len(index)),
            index=index,
            name='Sentiment_Score'
        )
        # Save synthetic data so it loads faster next time and doesn't change on every run
        synthetic_sentiment.to_pickle(SENTIMENT_FILE)
        return synthetic_sentiment

def train_and_evaluate_model():
    """
    Loads data, prepares features and labels, trains a Random Forest model,
    and prints performance metrics.
    """
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Data file not found at {INPUT_FILE}. Please run data_fetcher.py first.")
        return

    print(f"-> Loading financial data from {INPUT_FILE}...")
    data = pd.read_pickle(INPUT_FILE)
    
    # FIX for MergeError: If the loaded data has a MultiIndex (2 levels), 
    # it conflicts with the single-index sentiment data. We simplify the index
    # to just the date/time level.
    if data.index.nlevels > 1:
        data = data.droplevel(1)
        
    # --- NEW STEP: INTEGRATE SCRAPED SENTIMENT DATA ---
    # Call the helper function to get or generate the sentiment time-series
    sentiment_data = get_sentiment_data(data.index)
    # Join the sentiment scores to the main data frame
    data = data.join(sentiment_data, how='left')
    # Fill any missing sentiment values with 0 (neutral) for simplicity
    data['Sentiment_Score'].fillna(0, inplace=True)
    # --------------------------------------------------

    # 1. Feature Engineering: Create the prediction target (Label)
    # Target = 1 if the 'Close' price increases the next day, 0 otherwise.
    data[TARGET_COL] = (data['Close'].shift(-1) > data['Close']).astype(int)

    # 2. Feature Engineering: Create predictive features (X)
    # Use closing price and volume from the previous N_DAYS
    features = []
    for i in range(1, N_DAYS + 1):
        data[f'Close_Lag_{i}'] = data['Close'].shift(i)
        data[f'Volume_Lag_{i}'] = data['Volume'].shift(i)
        features.extend([f'Close_Lag_{i}', f'Volume_Lag_{i}'])

    # Add the 20-day Simple Moving Average (SMA) as a feature
    features.append('SMA_20')
    
    # --- NEW STEP: ADD SENTIMENT SCORE TO FEATURES ---
    features.append('Sentiment_Score')
    # -------------------------------------------------

    # Drop any rows that contain NaN values (due to shifting/lagging)
    data.dropna(inplace=True)

    X = data[features]
    y = data[TARGET_COL]

    print(f"-> Data prepared. Features used: {len(features)}. Total samples: {len(X)}")
    
    # 3. Split the data into training and testing sets (80/20 split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False, stratify=None
    )

    # 4. Initialize and Train the Model
    print("-> Training Random Forest Classifier...")
    # FIX: Corrected model name from RandomForestForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    # 5. Make Predictions and Evaluate
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print("\n--- Model Evaluation ---")
    print(f"Accuracy Score: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Price Down', 'Price Up']))
    
    print("\nMachine learning process complete.")


if __name__ == "__main__":
    train_and_evaluate_model()

