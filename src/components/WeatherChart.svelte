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
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { 
            label: 'Max °C', 
            data: maxData, 
            borderColor: '#ef4444', 
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            tension: 0.4, 
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#ef4444',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
          },
          { 
            label: 'Min °C', 
            data: minData, 
            borderColor: '#3b82f6', 
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4, 
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#3b82f6',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
          legend: { 
            position: 'top',
            labels: { font: { size: 12, weight: 'bold' }, padding: 15 }
          },
          filler: { propagate: false }
        },
        scales: { 
          y: { 
            beginAtZero: false,
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  onMount(() => {
    if (labels.length > 0) createChart();
  });

  $: if (labels && labels.length && canvasEl) {
    createChart();
  }

  onDestroy(() => { if (chart) chart.destroy(); });
</script>

<div style="width:100%; height:400px;">
  <canvas bind:this={canvasEl}></canvas>
</div>
