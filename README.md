# Weather Forecast App

A modern weather forecasting application that combines real-time weather data with machine learning predictions. This app fetches historical and current weather data from Open-Meteo and uses various time-series forecasting models to predict future temperature trends.

## Features

- **Multi-City Weather Tracking**: View weather data for San Francisco, New York, London, and Tokyo
- **Historical Weather Data**: Access up to 60 days of past weather data
- **ML-Powered Forecasting**: Multiple forecasting methods including:
  - Naive Mean (simple average baseline)
  - Naive Seasonal (seasonal patterns)
  - ARIMA (AutoRegressive Integrated Moving Average)
  - AutoETS (Exponential Smoothing)
- **Interactive Charts**: Visualize daily temperature trends
- **Responsive Design**: Works seamlessly across desktop and mobile devices

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Browser                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │     Svelte Weather App (Frontend)                            │   │
│  │  ┌─────────────────┐         ┌──────────────────────────┐    │   │
│  │  │ City Selection  │ ──────► │ Chart.js Visualizations  │    │   │
│  │  ├─────────────────┤         ├──────────────────────────┤    │   │
│  │  │ Forecast Config │         │ Daily Charts             │    │   │
│  │  └─────────────────┘         └──────────────────────────┘    │   │
│  └────────┬──────────────────────────────────────────────┬──────┘   │
└───────────┼──────────────────────────────────────────────┼──────────┘
            │ (1) Fetch Weather Data                       │
            │                                              │ (2) Forecast Request
            │                                              │
    ┌───────▼──────────────┐                    ┌──────────▼──────────────┐
    │  Open-Meteo API      │                    │  Google Cloud Function  │
    │  ├─ Daily Max/Min    │                    │  (Python Flask)         │
    │  └─ 60 Days History  │                    │  ┌──────────────────┐   │
    └──────────────────────┘                    │  │ Darts Models:    │   │
                                                │  ├─ NaiveMean       │   │
                                                │  ├─ NaiveSeasonal   │   │
                                                │  ├─ ARIMA           │   │
                                                │  ├─ AutoETS         │   │
                                                │  └──────────────────┘   │
                                                │  (3) Returns Forecast   │
                                                └─────────────────────────┘
```

**Data Flow:**
1. User selects city and forecast parameters in UI
2. App fetches historical weather data from Open-Meteo API
3. Historical data sent to Cloud Function for ML forecasting
4. Multiple models generate temperature predictions
5. Results visualized in interactive charts

## Tech Stack

**Frontend:**
- Svelte 4 (reactive UI framework)
- Chart.js (data visualization)
- Vite (build tool)

**Backend:**
- Python with Flask
- Darts (time-series forecasting library)
- Google Cloud Functions (serverless deployment)

**Data Source:**
- Open-Meteo API (free weather data)

## Getting Started

### Prerequisites
- Node.js (v16+)
- npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Cloud Function Setup

The forecasting backend runs on Google Cloud Functions. Deploy your own:

```bash
cd cloud-function
gcloud functions deploy simple-predict --runtime python312 --trigger-http --allow-unauthenticated
```

Update the `CLOUD_FUNCTION_URL` in [src/App.svelte](src/App.svelte) with your deployed function URL.

## Created by

Jason Yang

## License

MIT
