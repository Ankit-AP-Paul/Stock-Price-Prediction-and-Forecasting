from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, date, timedelta
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv1D,
    MaxPooling1D,
    Bidirectional,
    LSTM,
    Dense,
    Dropout
)
import warnings
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
warnings.filterwarnings('ignore')

app = FastAPI(
    title="Stock Price Prediction API",
    description="Simple API with health check and stock prediction endpoints",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Constants
LOOK_BACK = 60

# Pydantic models


class PredictRequest(BaseModel):
    ticker: str
    days: Optional[int] = 30


class StockPrediction(BaseModel):
    date: str
    actual_price: float
    predicted_price: float


class PredictResponse(BaseModel):
    ticker: str
    predictions: List[StockPrediction]
    metrics: dict


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    message: str


def get_technical_indicators(dataset):
    """Calculate technical indicators for the dataset"""
    # Create 7 and 21 days Moving Average
    dataset['ma7'] = dataset['Price'].rolling(window=7).mean()
    dataset['ma21'] = dataset['Price'].rolling(window=21).mean()

    # Create MACD
    dataset['26ema'] = dataset['Price'].ewm(span=26).mean()
    dataset['12ema'] = dataset['Price'].ewm(span=12).mean()
    dataset['MACD'] = dataset['12ema'] - dataset['26ema']

    # Create Bollinger Bands
    dataset['20sd'] = dataset['Price'].rolling(window=21).std()
    dataset['upper_band'] = dataset['ma21'] + (dataset['20sd'] * 2)
    dataset['lower_band'] = dataset['ma21'] - (dataset['20sd'] * 2)

    # Create Exponential moving average
    dataset['ema'] = dataset['Price'].ewm(com=0.5).mean()

    # Create Momentum
    dataset['momentum'] = dataset['Price'] - 1
    momentum_safe = dataset['momentum'].replace(0, 1e-8)
    momentum_safe = momentum_safe.where(momentum_safe > 0, 1e-8)
    dataset['log_momentum'] = np.log(momentum_safe)

    return dataset


def fetch_stock_data(ticker: str, start_date: str, end_date: str = None):
    """Fetch stock data from Yahoo Finance"""
    try:
        if end_date is None:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        start_date = datetime.strptime(start_date, "%Y-%m-%d")

        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)

        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        data = data[['Close']]
        data.columns = ['Price']

        return data
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


def create_and_train_model(X_train, y_train, n_features):
    """Create and train the CNN-BiLSTM model"""
    model = Sequential([
        # Convolutional layers for feature extraction
        Conv1D(filters=64, kernel_size=3, activation='relu',
               input_shape=(LOOK_BACK, n_features)),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=32, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),

        # Bidirectional LSTM layers for sequence modeling
        Bidirectional(LSTM(50, return_sequences=True)),
        Bidirectional(LSTM(25)),

        # Dense layers for final prediction
        Dense(16, activation='relu'),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Early stopping callback
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=10, restore_best_weights=True
    )

    # Train the model
    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=64,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=0
    )

    return model


def prepare_sequences(data, look_back: int):
    """Prepare sequences for training/testing"""
    X, y = [], []
    for i in range(look_back, len(data)):
        X.append(data[i-look_back:i])
        y.append(data[i, 0])
    return np.array(X), np.array(y)


def validate_ticker(ticker: str):
    """Validate if ticker exists"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        return not hist.empty
    except:
        return False


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        message="Stock Prediction API is running successfully"
    )


@app.post("/predict", response_model=PredictResponse)
async def predict_stock(request: PredictRequest):
    """Predict stock prices using CNN-BiLSTM model"""
    ticker = request.ticker.upper()

    # Validate ticker
    if not validate_ticker(ticker):
        raise HTTPException(
            status_code=404, detail=f"Ticker {ticker} not found or invalid")

    try:
        # Calculate date range for fetching data
        end_date = date.today()
        # Get extra data for training (2 years) + prediction period
        start_date = (end_date - timedelta(days=730 +
                      request.days)).strftime("%Y-%m-%d")

        # Fetch stock data
        data = fetch_stock_data(ticker, start_date)

        if len(data) < 200:  # Minimum data requirement
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data for {ticker}. Need at least 200 data points, got {len(data)}"
            )

        # Calculate technical indicators
        df = get_technical_indicators(data)
        df = df.dropna()

        if len(df) < LOOK_BACK + 50:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data after technical indicators calculation for {ticker}"
            )

        # Split data - use 80% for training, 20% for testing/prediction
        split_idx = int(len(df) * 0.8)
        data_training = df.iloc[:split_idx].copy()
        data_testing = df.iloc[split_idx:].copy()

        # Limit testing data to requested days
        if len(data_testing) > request.days:
            data_testing = data_testing.tail(request.days)

        # Scale training data
        scaler = MinMaxScaler()
        data_training_scaled = scaler.fit_transform(data_training)

        # Prepare training sequences
        X_train, y_train = prepare_sequences(data_training_scaled, LOOK_BACK)

        if len(X_train) == 0:
            raise HTTPException(
                status_code=400, detail=f"Cannot create training sequences for {ticker}")

        # Create and train model
        n_features = data_training_scaled.shape[1]
        model = create_and_train_model(X_train, y_train, n_features)

        # Prepare test data
        # Combine last LOOK_BACK rows of training with testing data
        past_data = data_training.tail(LOOK_BACK)
        combined_data = pd.concat([past_data, data_testing], ignore_index=True)

        # Scale combined data
        combined_scaled = scaler.transform(combined_data)

        # Prepare test sequences
        X_test, y_test = prepare_sequences(combined_scaled, LOOK_BACK)

        if len(X_test) == 0:
            raise HTTPException(
                status_code=400, detail=f"Cannot create test sequences for {ticker}")

        # Make predictions
        y_pred = model.predict(X_test, verbose=0)

        # Rescale predictions and actual values
        scale = 1 / scaler.scale_[0]
        y_pred_rescaled = y_pred.flatten() * scale
        y_test_rescaled = y_test * scale

        # Prepare response
        predictions = []
        test_dates = data_testing.index[:len(y_pred_rescaled)]

        for date_val, actual, predicted in zip(test_dates, y_test_rescaled, y_pred_rescaled):
            predictions.append(StockPrediction(
                date=date_val.strftime("%Y-%m-%d"),
                actual_price=round(float(actual), 2),
                predicted_price=round(float(predicted), 2)
            ))

        # Calculate metrics

        mse = mean_squared_error(y_test_rescaled, y_pred_rescaled)
        mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
        r2 = r2_score(y_test_rescaled, y_pred_rescaled)

        # Calculate accuracy percentage (inverse of MAPE)
        mape = np.mean(
            np.abs((y_test_rescaled - y_pred_rescaled) / y_test_rescaled)) * 100
        accuracy = max(0, 100 - mape)

        metrics = {
            "mse": round(float(mse), 2),
            "mae": round(float(mae), 2),
            "r2_score": round(float(r2), 4),
            "accuracy_percentage": round(float(accuracy), 2),
            "total_predictions": len(predictions),
            "prediction_period": f"{predictions[0].date} to {predictions[-1].date}" if predictions else "N/A"
        }

        return PredictResponse(
            ticker=ticker,
            predictions=predictions,
            metrics=metrics
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Prediction failed for {ticker}: {str(e)}")
