# Svelte + Open-Meteo Demo

Lightweight demo showing how to fetch daily weather data from the free Open-Meteo API and visualize it with Svelte + Chart.js.

Quick start

1. Install dependencies

```bash
npm install
```

2. Run dev server

```bash
npm run dev
```

Open http://localhost:5173 and try changing coordinates (default is New York City).

This demo now includes an hourly forecast visualization (temperature line + precipitation bars).

Files added

- [package.json](package.json)
- [index.html](index.html)
- [src/main.js](src/main.js)
- [src/App.svelte](src/App.svelte)
- [src/components/WeatherChart.svelte](src/components/WeatherChart.svelte)

Next steps

- Commit the scaffold and tweak styling or add more visualizations (hourly, precipitation probability, icons for weather codes).
