import functions_framework
from flask import Request, jsonify
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
import traceback

@functions_framework.http
def forecast_weather(request: Request):
    """
    HTTP Cloud Function that forecasts weather values using sklearn.
    
    Expected JSON payload:
    {
        "sequence": [23.5, 24.1, 23.8, 25.2, 26.1],
        "forecast_steps": 7,
        "method": "linear"  # "linear", "polynomial", or "random_forest"
    }
    
    Returns:
    {
        "forecast": [26.8, 27.2, 27.6, 28.0, 28.4, 28.8, 29.2],
        "confidence": 0.85,
        "status": "success"
    }
    """
    try:
        # Parse request JSON
        request_json = request.get_json(silent=True) or {}
        
        # Validate input
        sequence = request_json.get('sequence')
        forecast_steps = request_json.get('forecast_steps', 7)
        method = request_json.get('method', 'linear')
        
        if not sequence or len(sequence) < 3:
            return jsonify({
                'status': 'error',
                'message': 'sequence must have at least 3 values'
            }), 400
        
        if method not in ['linear', 'polynomial', 'random_forest']:
            return jsonify({
                'status': 'error',
                'message': f'method must be one of: linear, polynomial, random_forest. Got: {method}'
            }), 400
        
        # Convert to numpy array
        y = np.array(sequence, dtype=float)
        X = np.arange(len(y)).reshape(-1, 1)
        
        # Train model based on method
        if method == 'polynomial':
            # Polynomial regression (degree 2)
            poly = PolynomialFeatures(degree=2)
            X_poly = poly.fit_transform(X)
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Forecast future values
            future_X = np.arange(len(y), len(y) + forecast_steps).reshape(-1, 1)
            future_X_poly = poly.transform(future_X)
            forecast = model.predict(future_X_poly)
            
        elif method == 'random_forest':
            # Random Forest for non-linear patterns
            model = RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5)
            model.fit(X, y)
            
            # Forecast future values
            future_X = np.arange(len(y), len(y) + forecast_steps).reshape(-1, 1)
            forecast = model.predict(future_X)
            
        else:
            # Linear regression (default)
            model = LinearRegression()
            model.fit(X, y)
            
            # Forecast future values
            future_X = np.arange(len(y), len(y) + forecast_steps).reshape(-1, 1)
            forecast = model.predict(future_X)
        
        # Calculate R² score as confidence indicator
        score = model.score(X, y)
        confidence = max(0, min(1, score))  # Clamp between 0 and 1
        
        return jsonify({
            'status': 'success',
            'forecast': forecast.tolist(),
            'confidence': float(confidence),
            'input_length': len(sequence),
            'forecast_steps': forecast_steps,
            'method': method
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
