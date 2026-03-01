<script>
  import { onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  Chart.register(...registerables);

  export let labels = [];
  export let tempData = [];
  export let precipData = [];

  let canvasEl;
  let chart;

  function createChart() {
    const ctx = canvasEl.getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      data: {
        labels,
        datasets: [
          { type: 'line', label: 'Temp °C', data: tempData, borderColor: '#ef4444', yAxisID: 'y' , tension:0.2, fill:false},
          { type: 'bar', label: 'Precip mm', data: precipData, backgroundColor: '#60a5fa', yAxisID: 'y1' }
        ]
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { position: 'top' } },
        scales: {
          y: { type: 'linear', display: true, position: 'left', title: { display: true, text: '°C' } },
          y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'mm' }, grid: { drawOnChartArea: false } }
        }
      }
    });
  }

  $: if (labels && labels.length) createChart();

  onDestroy(() => { if (chart) chart.destroy(); });
</script>

<div style="width:100%;">
  <canvas bind:this={canvasEl} width="800" height="240"></canvas>
</div>
