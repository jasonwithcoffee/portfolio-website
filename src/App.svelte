<script>
  import { onMount } from 'svelte';
  import WeatherChart from './components/WeatherChart.svelte';
  import HourlyChart from './components/HourlyChart.svelte';

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

  async function fetchWeather() {
    loading = true; error = '';
    lastStatus = 'starting';
    console.log('fetchWeather start', { latitude, longitude, timezone });
    labels = []; tempsMax = []; tempsMin = []; weathercodes = [];
    try {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}` +
        `&daily=temperature_2m_max,temperature_2m_min,weathercode` +
        `&hourly=temperature_2m,precipitation,weathercode&timezone=${encodeURIComponent(timezone)}`;
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

  onMount(() => { fetchWeather(); });
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
  h1 { color: #fff; margin-bottom: 0.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  .controls { 
    display:flex; 
    gap:1rem; 
    align-items:center; 
    margin-bottom:2rem; 
    flex-wrap:wrap;
    background: rgba(255,255,255,0.95);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  }
  input { 
    padding:0.6rem; 
    width:140px;
    border: 2px solid #e5e7eb;
    border-radius: 6px;
    font-size: 0.95rem;
  }
  input:focus { 
    outline: none; 
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  button { 
    padding:0.7rem 1.5rem;
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
  button:disabled { opacity: 0.6; cursor: not-allowed; }
  .grid { 
    display:grid; 
    grid-template-columns:1fr 300px; 
    gap:1.5rem;
  }
  .card { 
    background:#fff; 
    padding:2rem; 
    border-radius:12px; 
    box-shadow:0 8px 32px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
  }
  h3 { color: #667eea; margin-top: 1.5rem; margin-bottom: 1rem; }
  table { width:100%; border-collapse:collapse }
  td, th { 
    padding:0.75rem 0.5rem; 
    text-align:left;
    border-bottom: 1px solid #f0f0f0;
  }
  th { background: #f9fafb; font-weight: 600; color: #667eea; }
  tr:hover { background: #f9fafb; }
</style>

<main>
  <h1>Svelte + Open-Meteo Demo</h1>

  <div class="controls">
    <label>Latitude <input type="number" bind:value={latitude} step="0.0001" /></label>
    <label>Longitude <input type="number" bind:value={longitude} step="0.0001" /></label>
    <label>Timezone <input type="text" bind:value={timezone} /></label>
    <button on:click={fetchWeather} disabled={loading}>{loading ? 'Loading…' : 'Fetch'}</button>
  </div>

  <div style="margin-bottom:0.5rem">Status: {lastStatus} {loading ? '(loading)' : ''}</div>

  <div style="font-size:0.9rem; color:#444; margin-bottom:0.75rem">
    Debug: labels={labels.length}, max={tempsMax.length}, min={tempsMin.length}, hourly={hourlyLabels.length}
    {#if labels.length}
      — first: {labels[0]} / {tempsMax[0]}°C
    {/if}
  </div>

  {#if error}
    <div style="color:crimson">{error}</div>
  {/if}

  <div class="grid">
    <div class="card">
      {#if labels.length}
        <WeatherChart {labels} maxData={tempsMax} minData={tempsMin} />
        <h3>Hourly (next 48+ hours)</h3>
        <div style="margin-bottom:1rem">
          <!-- Hourly chart component (temperature + precipitation) -->
          {#if hourlyLabels.length}
            <HourlyChart labels={hourlyLabels} tempData={hourlyTemp} precipData={hourlyPrecip} />
          {/if}
        </div>
        <h3>Daily Data</h3>
        <table>
          <thead><tr><th>Date</th><th>Max</th><th>Min</th><th>Code</th></tr></thead>
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
      <h3>About</h3>
      <p>This demo fetches daily max/min temperatures and weather codes from the free Open-Meteo API and visualizes them with Chart.js inside a Svelte component.</p>
      <p>Try changing the coordinates to see different locations.</p>
    </div>
  </div>
</main>
