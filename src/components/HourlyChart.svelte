<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  Chart.register(...registerables);

  export let labels = [];
  export let tempData = [];
  export let precipData = [];

  let canvasEl;
  let chart;

  function createChart() {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          { 
            type: 'line', 
            label: 'Temperature °C', 
            data: tempData, 
            borderColor: '#f97316',
            backgroundColor: 'rgba(249, 115, 22, 0.05)',
            yAxisID: 'y',
            tension: 0.4,
            fill: true,
            pointRadius: 3,
            pointHoverRadius: 5,
            pointBackgroundColor: '#f97316',
            pointBorderColor: '#fff',
            pointBorderWidth: 1
          },
          { 
            type: 'bar', 
            label: 'Precipitation (mm)', 
            data: precipData, 
            backgroundColor: 'rgba(59, 130, 246, 0.7)',
            yAxisID: 'y1',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { 
          legend: { 
            position: 'top',
            labels: { font: { size: 12, weight: 'bold' }, padding: 15 }
          }
        },
        scales: {
          y: { 
            type: 'linear', 
            display: true, 
            position: 'left', 
            title: { display: true, text: '°C', font: { weight: 'bold' } },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          y1: { 
            type: 'linear', 
            display: true, 
            position: 'right', 
            title: { display: true, text: 'mm', font: { weight: 'bold' } }, 
            grid: { drawOnChartArea: false }
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

<div style="width:100%; height:300px;">
  <canvas bind:this={canvasEl}></canvas>
</div>
