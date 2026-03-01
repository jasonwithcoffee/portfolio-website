# Weather Forecasting Cloud Function

A Google Cloud Function that uses scikit-learn to forecast weather values on demand.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt
pip install functions-framework

# Run locally (listens on http://localhost:8080)
functions-framework --target=forecast_weather --debug
```

## Test Request

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "sequence": [23.5, 24.1, 23.8, 25.2, 26.1, 25.8, 26.3],
    "forecast_steps": 7,
    "method": "linear"
  }'
```

## Deploy to Google Cloud

```bash
gcloud functions deploy forecast_weather \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point forecast_weather \
  --source ./cloud-function
```

## Request Payload

```json
{
  "sequence": [23.5, 24.1, 23.8, 25.2, 26.1],
  "forecast_steps": 7,
  "method": "linear"
}
```

- `sequence`: Array of historical values (minimum 3 values)
- `forecast_steps`: Number of future steps to predict (default: 7)
- `method`: One of three forecasting methods:
  - `"linear"` - Simple linear regression (best for linear trends)
  - `"polynomial"` - Polynomial regression degree 2 (captures curved patterns)
  - `"random_forest"` - Random forest (captures complex non-linear patterns)

## Response

```json
{
  "status": "success",
  "forecast": [26.8, 27.2, 27.6, 28.0, 28.4, 28.8, 29.2],
  "confidence": 0.92,
  "input_length": 5,
  "forecast_steps": 7,
  "method": "linear"
}
```

- `forecast`: Array of predicted values
- `confidence`: R² score (0-1, how well the model fits the input data)
- `input_length`: Number of historical values used
- `forecast_steps`: Number of predictions returned
- `method`: Which forecasting method was used

## Forecasting Methods Explained

### Linear Regression
- **Best for**: Steady upward/downward trends
- **Speed**: Fastest
- **Example**: Temperature slowly rising day by day

### Polynomial Regression
- **Best for**: Curved trends (e.g., U-shaped or bell-shaped patterns)
- **Speed**: Fast
- **Example**: Temperature dips in morning, peaks at noon, dips again at night

### Random Forest
- **Best for**: Complex, non-linear patterns with multiple features
- **Speed**: Moderate
- **Example**: Weather with cyclical and irregular patterns
