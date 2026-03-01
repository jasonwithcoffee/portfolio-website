<script>
  import { onMount } from 'svelte';
  import WeatherChart from './components/WeatherChart.svelte';

  const cities = {
    'San Francisco': { lat: 37.7749, lon: -122.4194, tz: 'America/Los_Angeles' },
    'New York': { lat: 40.7128, lon: -74.0060, tz: 'America/New_York' },
    'London': { lat: 51.5074, lon: -0.1278, tz: 'Europe/London' },
    'Tokyo': { lat: 35.6762, lon: 139.6503, tz: 'Asia/Tokyo' }
  };

  let selectedCity = 'San Francisco';
  let latitude = 37.7749;
  let longitude = -122.4194;
  let timezone = 'America/Los_Angeles';
  let loading = false;
  let error = '';
  let lastStatus = '';

  let labels = [];
  let tempsMax = [];
  let tempsMin = [];
  let weathercodes = [];

  // hourly
  let hourlyLabels = [];
  let hourlyTempMax = [];
  let hourlyTempMin = [];
  let hourlyPrecip = [];

  // Last 7 days summary
  let last7Days = [];

  // ML Forecasting
  let forecastMethod = 'naive_mean';
  let forecastSteps = 7;
  let forecastLoading = false;
  let forecastError = '';
  let forecastMax = null;
  let forecastMin = null;
  let forecastConfidence = 0;
  
  // Model-specific parameters
  let seasonLength = null; // For naive_seasonal
  let arimaP = 1; // For ARIMA
  let arimaD = 1; // For ARIMA
  let arimaQ = 1; // For ARIMA
  
  const CLOUD_FUNCTION_URL = 'https://simple-predict-297426001108.us-west1.run.app'; // Change to your deployed Cloud Function URL

  function updateCity(city) {
    selectedCity = city;
    const cityData = cities[city];
    latitude = cityData.lat;
    longitude = cityData.lon;
    timezone = cityData.tz;
    fetchWeather();
  }

  async function fetchWeather() {
    loading = true;
    error = '';
    lastStatus = 'starting';
    console.log('fetchWeather start', { latitude, longitude, timezone });
    labels = [];
    tempsMax = [];
    tempsMin = [];
    weathercodes = [];
    try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=${encodeURIComponent(timezone)}&past_days=60&forecast_days=0`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      console.log('fetchWeather response', { ok: res.ok, size: JSON.stringify(data).length });
      if (data?.daily) {
        labels = data.daily.time || [];
        tempsMax = data.daily.temperature_2m_max || [];
        tempsMin = data.daily.temperature_2m_min || [];
        weathercodes = data.daily.weathercode || [];

        // Calculate last 7 days (past 7 days from today)
        const pastDaysCount = data.daily.time.findIndex(d => d >= new Date().toISOString().split('T')[0]) || 0;
        const last7StartIdx = Math.max(0, pastDaysCount - 7);
        const last7EndIdx = pastDaysCount;
        
        last7Days = [];
        for (let i = last7StartIdx; i < last7EndIdx && i < labels.length; i++) {
          last7Days.push({
            date: labels[i],
            max: tempsMax[i],
            min: tempsMin[i],
            weathercode: weathercodes[i]
          });
        }
        // If we don't have enough past data, show what we have
        if (last7Days.length === 0 && labels.length > 0) {
          const endIdx = Math.min(7, labels.length);
          for (let i = 0; i < endIdx; i++) {
            last7Days.push({
              date: labels[i],
              max: tempsMax[i],
              min: tempsMin[i],
              weathercode: weathercodes[i]
            });
          }
        }
      }

      lastStatus = 'done';
      console.log('fetchWeather populated', {
        labels: labels.length,
        tempsMax: tempsMax.length,
        tempsMin: tempsMin.length,
        hourly: hourlyLabels.length
      });
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    fetchWeather();
  });

  async function generateForecast() {
    if (tempsMax.length === 0 || tempsMin.length === 0) {
      forecastError = 'Please load weather data first';
      return;
    }

    forecastLoading = true;
    forecastError = '';
    forecastMax = null;
    forecastMin = null;

    try {
      // Build request body with model parameters
      const requestBody = {
        forecast_steps: forecastSteps,
        method: forecastMethod
      };
      
      // Add model-specific parameters
      if (forecastMethod === 'naive_seasonal' && seasonLength !== null) {
        requestBody.season_length = seasonLength;
      }
      if (forecastMethod === 'arima') {
        requestBody.arima_p = arimaP;
        requestBody.arima_d = arimaD;
        requestBody.arima_q = arimaQ;
      }
      
      // Use daily min/max temperature data for forecasting
      const [maxResponse, minResponse] = await Promise.all([
        fetch(CLOUD_FUNCTION_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sequence: tempsMax,
            ...requestBody
          })
        }),
        fetch(CLOUD_FUNCTION_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sequence: tempsMin,
            ...requestBody
          })
        })
      ]);

      if (!maxResponse.ok) throw new Error(`HTTP ${maxResponse.status} for max forecast`);
      if (!minResponse.ok) throw new Error(`HTTP ${minResponse.status} for min forecast`);
      
      const maxData = await maxResponse.json();
      const minData = await minResponse.json();

      if (maxData.status === 'success' && minData.status === 'success') {
        forecastMax = maxData.forecast;
        forecastMin = minData.forecast;
        forecastConfidence = (maxData.confidence + minData.confidence) / 2;
      } else {
        forecastError = maxData.message || minData.message || 'Forecast failed';
      }
    } catch (e) {
      forecastError = `Error: ${e.message}`;
    } finally {
      forecastLoading = false;
    }
  }
</script>

<style>
  main { 
    font-family: system-ui, Arial; 
    padding: 2rem; 
    max-width: 1200px; 
    margin: 0 auto;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
  }
  h1 { 
    color: #fff; 
    margin-bottom: 0.5rem; 
    text-shadow: 0 2px 4px rgba(0,0,0,0.1); 
  }
  .controls { 
    display: flex; 
    gap: 1rem; 
    align-items: center; 
    margin-bottom: 2rem; 
    flex-wrap: wrap;
    background: rgba(255,255,255,0.95);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  }
  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  select {
    padding: 0.6rem;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    font-size: 0.95rem;
    background: white;
    cursor: pointer;
  }
  select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  button { 
    padding: 0.7rem 1.5rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  button:hover:not(:disabled) { 
    background: #5568d3;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  button:disabled { 
    opacity: 0.6; 
    cursor: not-allowed; 
  }
  .grid { 
    display: grid; 
    grid-template-columns: 1fr; 
    gap: 1.5rem;
  }
  .card { 
    background: #fff; 
    padding: 2rem; 
    border-radius: 12px; 
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
  }
  h3 { 
    color: #667eea; 
    margin-top: 1.5rem; 
    margin-bottom: 1rem; 
  }
  table { 
    width: 100%; 
    border-collapse: collapse;
  }
  td, th { 
    padding: 0.75rem 0.5rem; 
    text-align: left;
    border-bottom: 1px solid #f0f0f0;
  }
  th { 
    background: #f9fafb; 
    font-weight: 600; 
    color: #667eea; 
  }
  tr:hover { 
    background: #f9fafb; 
  }
</style>

<main>
  <div style="margin-bottom: 1.5rem;">
    <h1>Weather Forecast App</h1>
    <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0; font-size: 0.95rem;">
      ML-powered weather forecasting using real-time data and time-series predictions
    </p>
    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.85rem; margin-top: 0.5rem;">
      Created by Jason Yang
    </p>
  </div>

  <div class="controls">
    <label>
      City
      <select bind:value={selectedCity} on:change={(e) => updateCity(e.target.value)}>
        {#each Object.keys(cities) as city}
          <option value={city}>{city}</option>
        {/each}
      </select>
    </label>
    <button on:click={fetchWeather} disabled={loading}>
      {loading ? 'Loading…' : 'Refresh'}
    </button>
  </div>

  <div class="controls">
    <label>
      Forecast Method
      <select bind:value={forecastMethod}>
        <option value="naive_mean">Naive Mean</option>
        <option value="naive_seasonal">Naive Seasonal</option>
        <option value="arima">ARIMA</option>
        <option value="autoets">AutoETS</option>
      </select>
    </label>
    <label>
      Forecast Steps
      <input type="number" bind:value={forecastSteps} min="1" max="30" style="width: 80px; padding: 0.6rem;" />
    </label>
    
    {#if forecastMethod === 'naive_seasonal'}
      <label>
        Season Length (optional)
        <input type="number" bind:value={seasonLength} min="1" placeholder="auto" style="width: 100px; padding: 0.6rem;" />
      </label>
    {/if}
    
    {#if forecastMethod === 'arima'}
      <label>
        p <input type="number" bind:value={arimaP} min="0" max="5" style="width: 50px; padding: 0.6rem;" />
      </label>
      <label>
        d <input type="number" bind:value={arimaD} min="0" max="2" style="width: 50px; padding: 0.6rem;" />
      </label>
      <label>
        q <input type="number" bind:value={arimaQ} min="0" max="5" style="width: 50px; padding: 0.6rem;" />
      </label>
    {/if}
    
    <button 
      on:click={generateForecast}
      style="background: linear-gradient(135deg, #3b82f6, #1e40af); font-size: 1rem; padding: 0.8rem 2rem;"
    >
      Generate Forecast
    </button>
  </div>

  {#if error}
    <div style="color: crimson;">{error}</div>
  {/if}

  {#if forecastError}
    <div style="color: crimson; margin-bottom: 1rem;">{forecastError}</div>
  {/if}

  <div class="grid">
    <div class="card">
      {#if labels.length}
        <WeatherChart {labels} maxData={tempsMax} minData={tempsMin} {forecastMax} {forecastMin} />
      {:else}
        <div>Loading data or no data available.</div>
      {/if}
    </div>
  </div>
</main>
