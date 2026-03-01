<script>
  import { onMount } from 'svelte';
  import WeatherChart from './components/WeatherChart.svelte';
  import HourlyChart from './components/HourlyChart.svelte';

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
  let hourlyTemp = [];
  let hourlyPrecip = [];

  // ML Forecasting
  let forecastMethod = 'linear';
  let forecastSteps = 7;
  let forecastLoading = false;
  let forecastError = '';
  let forecast = null;
  let forecastConfidence = 0;
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
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&daily=temperature_2m_max,temperature_2m_min,weathercode&hourly=temperature_2m,precipitation,weathercode&timezone=${encodeURIComponent(timezone)}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      console.log('fetchWeather response', { ok: res.ok, size: JSON.stringify(data).length });
      if (data?.daily) {
        labels = data.daily.time || [];
        tempsMax = data.daily.temperature_2m_max || [];
        tempsMin = data.daily.temperature_2m_min || [];
        weathercodes = data.daily.weathercode || [];
      }

      if (data?.hourly) {
        hourlyLabels = data.hourly.time || [];
        hourlyTemp = data.hourly.temperature_2m || [];
        hourlyPrecip = data.hourly.precipitation || [];
      } else {
        error = 'No daily data returned from API.';
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
    if (tempsMax.length === 0) {
      forecastError = 'Please load weather data first';
      return;
    }

    forecastLoading = true;
    forecastError = '';
    forecast = null;

    try {
      const response = await fetch(CLOUD_FUNCTION_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sequence: tempsMax,
          forecast_steps: forecastSteps,
          method: forecastMethod
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();

      if (data.status === 'success') {
        forecast = data.forecast;
        forecastConfidence = data.confidence;
      } else {
        forecastError = data.message || 'Forecast failed';
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
    grid-template-columns: 1fr 300px; 
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
  <h1>Svelte + Open-Meteo Demo</h1>

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
        <option value="linear">Linear</option>
        <option value="polynomial">Polynomial</option>
        <option value="random_forest">Random Forest</option>
      </select>
    </label>
    <label>
      Forecast Steps
      <input type="number" bind:value={forecastSteps} min="1" max="30" style="width: 80px; padding: 0.6rem;" />
    </label>
    <button on:click={generateForecast} disabled={forecastLoading || tempsMax.length === 0}>
      {forecastLoading ? 'Generating…' : 'Generate Forecast'}
    </button>
  </div>

  <div style="margin-bottom: 0.5rem;">
    Status: {lastStatus} {loading ? '(loading)' : ''}
  </div>

  <div style="font-size: 0.9rem; color: #444; margin-bottom: 0.75rem;">
    Debug: labels={labels.length}, max={tempsMax.length}, min={tempsMin.length}, hourly={hourlyLabels.length}
    {#if labels.length}
      — first: {labels[0]} / {tempsMax[0]}°C
    {/if}
  </div>

  {#if error}
    <div style="color: crimson;">{error}</div>
  {/if}

  {#if forecastError}
    <div style="color: crimson; margin-bottom: 1rem;">{forecastError}</div>
  {/if}

  {#if forecast}
    <div class="card" style="margin-bottom: 1.5rem; background: #f0f9ff; border-left: 4px solid #667eea;">
      <h3>ML Forecast Results ({forecastMethod})</h3>
      <p><strong>Confidence:</strong> {(forecastConfidence * 100).toFixed(1)}%</p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.75rem; margin-top: 1rem;">
        {#each forecast as value, i}
          <div style="background: white; padding: 1rem; border-radius: 6px; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 0.85rem; color: #666;">Day +{i + 1}</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">{value.toFixed(1)}°C</div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <div class="grid">
    <div class="card">
      {#if labels.length}
        <WeatherChart {labels} maxData={tempsMax} minData={tempsMin} />
        <h3>Hourly (next 48+ hours)</h3>
        <div style="margin-bottom: 1rem;">
          {#if hourlyLabels.length}
            <HourlyChart 
              labels={hourlyLabels} 
              tempData={hourlyTemp} 
              precipData={hourlyPrecip} 
            />
          {/if}
        </div>
        <h3>Daily Data</h3>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Max</th>
              <th>Min</th>
              <th>Code</th>
            </tr>
          </thead>
          <tbody>
            {#each labels as label, i}
              <tr>
                <td>{label}</td>
                <td>{tempsMax[i]}</td>
                <td>{tempsMin[i]}</td>
                <td>{weathercodes[i]}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else}
        <div>Loading data or no data available.</div>
      {/if}
    </div>

    <div class="card">
      <h3>Weather Comparison</h3>
      <p>Select a city to view its weather forecast from the free Open-Meteo API.</p>
      <p><strong>Available cities:</strong></p>
      <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
        <li>San Francisco</li>
        <li>New York</li>
        <li>London</li>
        <li>Tokyo</li>
      </ul>
    </div>
  </div>
</main>
