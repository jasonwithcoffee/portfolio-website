<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  Chart.register(...registerables);

  export let labels = [];
  export let maxData = [];
  export let minData = [];

  let canvasEl;
  let chart;

  function createChart() {
    const ctx = canvasEl.getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: 'Max °C', data: maxData, borderColor: '#ef4444', tension: 0.2, fill:false },
          { label: 'Min °C', data: minData, borderColor: '#3b82f6', tension: 0.2, fill:false }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'top' } },
        scales: { y: { beginAtZero: false } }
      }
    });
  }

  $: if (labels && labels.length) {
    // ensure chart updates when data changes
    createChart();
  }

  onDestroy(() => { if (chart) chart.destroy(); });
</script>

<div style="width:100%;">
  <canvas bind:this={canvasEl} width="600" height="300"></canvas>
</div>
