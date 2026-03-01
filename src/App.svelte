<script>
  import { onMount } from 'svelte';
  import WeatherChart from './components/WeatherChart.svelte';
  import HourlyChart from './components/HourlyChart.svelte';

  let latitude = 40.7128;
  let longitude = -74.0060;
  let timezone = 'America/New_York';
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
  main { font-family: system-ui, Arial; padding: 1rem; max-width: 900px; margin: 0 auto; }
  .controls { display:flex; gap:0.5rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap }
  input { padding:0.4rem; width:140px }
  button { padding:0.5rem 0.8rem }
  .grid { display:grid; grid-template-columns:1fr 320px; gap:1rem }
  .card { background:#fff; padding:1rem; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.06) }
  table { width:100%; border-collapse:collapse }
  td, th { padding:0.25rem 0.5rem; text-align:left }
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
