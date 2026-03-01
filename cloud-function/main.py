import functions_framework
from flask import Request, jsonify
import numpy as np
import traceback
import warnings
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

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
    logger.info(f"forecast_naive_mean: sequence_len={len(sequence)}, forecast_steps={forecast_steps}")
    try:
        ts = TimeSeries.from_values(np.array(sequence, dtype=float))
        
        # Fit and forecast with NaiveMean
        model = NaiveMean()
        model.fit(ts)
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
        
        # Confidence based on data variance
        confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
        
        logger.info(f"forecast_naive_mean: success, confidence={confidence}")
        return forecast, confidence
    except Exception as e:
        logger.error(f"forecast_naive_mean failed: {str(e)}", exc_info=True)
        raise


def forecast_naive_seasonal(sequence, forecast_steps):
    """
    Forecast using Darts NaiveSeasonal (seasonal pattern)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    logger.info(f"forecast_naive_seasonal: sequence_len={len(sequence)}, forecast_steps={forecast_steps}")
    try:
        ts = TimeSeries.from_values(np.array(sequence, dtype=float))
        
        # NaiveSeasonal requires season_length < len(sequence)
        # Use half the sequence length as season, but at least 2
        season_length = max(2, len(sequence) // 2)
        if season_length >= len(sequence):
            season_length = len(sequence) - 1
        
        logger.info(f"forecast_naive_seasonal: calculated season_length={season_length}")
        
        # Fit and forecast with NaiveSeasonal
        # Pass season_length as positional argument
        model = NaiveSeasonal(season_length)
        model.fit(ts)
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
        
        # Confidence based on seasonality detection
        confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
        
        logger.info(f"forecast_naive_seasonal: success, confidence={confidence}")
        return forecast, confidence
    except Exception as e:
        logger.error(f"forecast_naive_seasonal failed: {str(e)}", exc_info=True)
        raise


def forecast_arima(sequence, forecast_steps):
    """
    Forecast using Darts ARIMA (AutoRegressive Integrated Moving Average)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    logger.info(f"forecast_arima: sequence_len={len(sequence)}, forecast_steps={forecast_steps}")
    try:
        ts = TimeSeries.from_values(np.array(sequence, dtype=float))
        
        # ARIMA needs sufficient data points
        # Validate sequence length for d=1 (differencing)
        if len(sequence) < 4:
            raise ValueError(f"ARIMA requires at least 4 data points for differencing, got {len(sequence)}")
        
        # Fit ARIMA model with conservative parameters
        # p=1, d=1, q=1 is standard for many time series
        logger.info("forecast_arima: fitting ARIMA(1,1,1)")
        model = ARIMA(p=1, d=1, q=1)
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
        
        # Confidence based on stability
        confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
        
        logger.info(f"forecast_arima: success, confidence={confidence}")
        return forecast, confidence
    except Exception as e:
        logger.error(f"forecast_arima failed: {str(e)}", exc_info=True)
        raise


def forecast_prophet(sequence, forecast_steps):
    """
    Forecast using Darts Prophet
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    logger.info(f"forecast_prophet: sequence_len={len(sequence)}, forecast_steps={forecast_steps}")
    try:
        import os
        
        # Suppress cmdstanpy output to avoid issues
        os.environ['STAN_BACKEND'] = 'CMDSTANPY'
        
        # Suppress cmdstanpy logging
        logging.getLogger('cmdstanpy').setLevel(logging.ERROR)
        logging.getLogger('prophet').setLevel(logging.ERROR)
        
        ts = TimeSeries.from_values(np.array(sequence, dtype=float))
        
        # Prophet benefits from more data but can work with less
        if len(sequence) < 5:
            raise ValueError(f"Prophet requires at least 5 data points, got {len(sequence)}")
        
        # Fit Prophet model with reasonable hyperparameters
        # yearly_seasonality=False and daily_seasonality=False since we have daily weather data
        logger.info("forecast_prophet: fitting Prophet model")
        model = Prophet(yearly_seasonality=False, daily_seasonality=False, interval_width=0.95)
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
        
        # Confidence based on stability
        confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
        
        logger.info(f"forecast_prophet: success, confidence={confidence}")
        return forecast, confidence
    except Exception as e:
        logger.error(f"forecast_prophet failed: {str(e)}", exc_info=True)
        raise


def forecast_autoets(sequence, forecast_steps):
    """
    Forecast using Darts AutoETS (Automatic Error-Trend-Seasonality)
    
    Args:
        sequence: List of numeric values
        forecast_steps: Number of steps to forecast
        
    Returns:
        Tuple of (forecast array, confidence score)
    """
    logger.info(f"forecast_autoets: sequence_len={len(sequence)}, forecast_steps={forecast_steps}")
    try:
        ts = TimeSeries.from_values(np.array(sequence, dtype=float))
        
        # AutoETS requires sufficient data for model estimation
        if len(sequence) < 5:
            raise ValueError(f"AutoETS requires at least 5 data points, got {len(sequence)}")
        
        # Check for any NaN or infinite values
        if np.isnan(sequence).any() or np.isinf(sequence).any():
            raise ValueError("Sequence contains NaN or infinite values")
        
        # Fit AutoETS model
        # AutoETS automatically selects error, trend, and seasonal components
        logger.info("forecast_autoets: fitting AutoETS model")
        model = AutoETS()
        model.fit(ts)
        
        # Forecast
        forecast_ts = model.predict(n=forecast_steps)
        forecast = forecast_ts.values().flatten()
        
        # Confidence based on fit quality
        confidence = max(0.5, min(1, 1 / (1 + np.std(sequence))))
        
        logger.info(f"forecast_autoets: success, confidence={confidence}")
        return forecast, confidence
    except Exception as e:
        logger.error(f"forecast_autoets failed: {str(e)}", exc_info=True)
        raise


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
        logger.info(f"Received request: method={request.method}")
        
        # Parse request JSON
        request_json = request.get_json(silent=True) or {}
        
        # Validate input
        sequence = request_json.get('sequence')
        forecast_steps = request_json.get('forecast_steps', 7)
        method = request_json.get('method', 'naive_mean')
        
        logger.info(f"Request params: method={method}, forecast_steps={forecast_steps}, sequence_len={len(sequence) if sequence else 0}")
        
        if not sequence or len(sequence) < 3:
            msg = 'sequence must have at least 3 values'
            logger.warning(f"Validation failed: {msg}")
            return set_cors_headers(jsonify({
                'status': 'error',
                'message': msg
            })), 400
        
        valid_methods = ['naive_mean', 'naive_seasonal', 'arima', 'prophet', 'autoets']
        if method not in valid_methods:
            msg = f'method must be one of: {", ".join(valid_methods)}. Got: {method}'
            logger.warning(f"Validation failed: {msg}")
            return set_cors_headers(jsonify({
                'status': 'error',
                'message': msg
            })), 400
        
        # Forecast based on method
        logger.info(f"Starting forecast with method={method}")
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
        
        logger.info(f"Forecast successful: method={method}, confidence={confidence}")
        return set_cors_headers(jsonify({
            'status': 'success',
            'forecast': forecast.tolist(),
            'confidence': float(confidence),
            'input_length': len(sequence),
            'forecast_steps': forecast_steps,
            'method': method
        })), 200
    
    except Exception as e:
        error_msg = str(e)
        tb = traceback.format_exc()
        logger.error(f"Request failed with error: {error_msg}")
        logger.error(f"Traceback:\n{tb}")
        return set_cors_headers(jsonify({
            'status': 'error',
            'message': error_msg,
            'traceback': tb
        })), 500

