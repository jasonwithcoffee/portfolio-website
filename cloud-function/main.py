import functions_framework
from flask import Request, jsonify
import numpy as np
import traceback
import warnings

# Darts models
from darts import TimeSeries
from darts.models import NaiveMean, NaiveSeasonal, ARIMA, Prophet, AutoETS

warnings.filterwarnings('ignore')

"""
Sample Curl
curl -X POST https://simple-predict-297426001108.us-west1.run.app \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": [23.5, 24.1, 23.8, 25.2, 26.1],
    "forecast_steps": 7,
    "method": "autoets"
  }' -v
"""

def set_cors_headers(response):
    """Add CORS headers to response"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def forecast_naive_mean(sequence, forecast_steps):
    """
    Forecast using Darts NaiveMean (simple average)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    ts = TimeSeries.from_values(np.array(sequence, dtype=float))
    
    # Fit and forecast with NaiveMean
    model = NaiveMean()
    model.fit(ts)
    forecast_ts = model.predict(n=forecast_steps)
    forecast = forecast_ts.values().flatten()
    
    # Confidence based on data variance
    confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
    
    return forecast, confidence


def forecast_naive_seasonal(sequence, forecast_steps):
    """
    Forecast using Darts NaiveSeasonal (seasonal pattern)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    ts = TimeSeries.from_values(np.array(sequence, dtype=float))
    
    # Fit and forecast with NaiveSeasonal
    model = NaiveSeasonal(season_length=max(2, len(sequence) // 3))
    model.fit(ts)
    forecast_ts = model.predict(n=forecast_steps)
    forecast = forecast_ts.values().flatten()
    
    # Confidence based on seasonality detection
    confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
    
    return forecast, confidence


def forecast_arima(sequence, forecast_steps):
    """
    Forecast using Darts ARIMA (AutoRegressive Integrated Moving Average)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    ts = TimeSeries.from_values(np.array(sequence, dtype=float))
    
    # Need at least 10 data points for ARIMA
    if len(sequence) < 10:
        # Fall back to NaiveMean for short sequences
        model = NaiveMean()
        model.fit(ts)
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    else:
        # Fit ARIMA model
        model = ARIMA(p=1, d=1, q=1)
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    
    # Confidence based on stability
    confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
    
    return forecast, confidence


def forecast_prophet(sequence, forecast_steps):
    """
    Forecast using Darts Prophet
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    ts = TimeSeries.from_values(np.array(sequence, dtype=float))
    
    # Need at least 10 data points for Prophet
    if len(sequence) < 10:
        # Fall back to NaiveMean for short sequences
        model = NaiveMean()
        model.fit(ts)
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    else:
        # Fit Prophet model
        model = Prophet()
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    
    # Confidence based on stability
    confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
    
    return forecast, confidence


def forecast_autoets(sequence, forecast_steps):
    """
    Forecast using Darts AutoETS (Automatic Error-Trend-Seasonality)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    ts = TimeSeries.from_values(np.array(sequence, dtype=float))
    
    # Need at least 10 data points for AutoETS
    if len(sequence) < 10:
        # Fall back to NaiveMean for short sequences
        model = NaiveMean()
        model.fit(ts)
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    else:
        # Fit AutoETS model
        model = AutoETS()
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
    
    # Confidence based on fit quality
    confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
    
    return forecast, confidence


@functions_framework.http
def forecast_weather(request: Request):
    """
    HTTP Cloud Function that forecasts weather values using Darts models.
    
    Expected JSON payload:
    {
        "sequence": [23.5, 24.1, 23.8, 25.2, 26.1],
        "forecast_steps": 7,
        "method": "naive_mean"  # "naive_mean", "naive_seasonal", "arima", "prophet", or "autoets"
    }
    
    Returns:
    {
        "forecast": [26.8, 27.2, 27.6, 28.0, 28.4, 28.8, 29.2],
        "confidence": 0.85,
        "status": "success"
    }
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return set_cors_headers(jsonify({})), 204
    
    try:
        # Parse request JSON
        request_json = request.get_json(silent=True) or {}
        
        # Validate input
        sequence = request_json.get('sequence')
        forecast_steps = request_json.get('forecast_steps', 7)
        method = request_json.get('method', 'naive_mean')
        
        if not sequence or len(sequence) < 3:
            return set_cors_headers(jsonify({
                'status': 'error',
                'message': 'sequence must have at least 3 values'
            })), 400
        
        valid_methods = ['naive_mean', 'naive_seasonal', 'arima', 'prophet', 'autoets']
        if method not in valid_methods:
            return set_cors_headers(jsonify({
                'status': 'error',
                'message': f'method must be one of: {", ".join(valid_methods)}. Got: {method}'
            })), 400
        
        # Forecast based on method
        if method == 'naive_mean':
            forecast, confidence = forecast_naive_mean(sequence, forecast_steps)
        elif method == 'naive_seasonal':
            forecast, confidence = forecast_naive_seasonal(sequence, forecast_steps)
        elif method == 'arima':
            forecast, confidence = forecast_arima(sequence, forecast_steps)
        elif method == 'prophet':
            forecast, confidence = forecast_prophet(sequence, forecast_steps)
        else:  # autoets
            forecast, confidence = forecast_autoets(sequence, forecast_steps)
        
        return set_cors_headers(jsonify({
            'status': 'success',
            'forecast': forecast.tolist(),
            'confidence': float(confidence),
            'input_length': len(sequence),
            'forecast_steps': forecast_steps,
            'method': method
        })), 200
    
    except Exception as e:
        return set_cors_headers(jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        })), 500

