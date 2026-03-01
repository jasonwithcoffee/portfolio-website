<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  Chart.register(...registerables);

  export let labels = [];
  export let maxData = [];
  export let minData = [];
  export let forecastMax = null;
  export let forecastMin = null;
  
  // Format hourly labels to show time only
  function formatHourlyLabels(labels) {
    return labels.map(label => {
      if (!label) return '';
      // Extract time portion from ISO datetime (HH:mm format)
      const parts = label.split('T');
      if (parts.length > 1) {
        return parts[1].substring(0, 5); // Get HH:mm
      }
      return label;
    });
  }

  let canvasEl;
  let chart;

  function createChart() {
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');
    if (chart) chart.destroy();
    
    const formattedLabels = formatHourlyLabels(labels);
    
    const datasets = [
      { 
        label: 'Max °C', 
        data: maxData,
        borderColor: '#ef4444', 
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4, 
        fill: true,
        pointRadius: 0,
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
        pointRadius: 0,
        pointHoverRadius: 6,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2
      }
    ];

    // Add forecast data if available
    let extendedLabels = [...formattedLabels];
    if ((forecastMax && forecastMax.length > 0) || (forecastMin && forecastMin.length > 0)) {
      const forecastLength = forecastMax?.length || forecastMin?.length || 0;
      const forecastLabels = Array.from({ length: forecastLength }, (_, i) => `+${i + 1}`);
      extendedLabels = [...extendedLabels, ...forecastLabels];
      
      // Extend max and min data with null values to align with new labels
      const paddedMaxData = [...maxData, ...Array(forecastLength).fill(null)];
      const paddedMinData = [...minData, ...Array(forecastLength).fill(null)];
      
      datasets[0].data = paddedMaxData;
      datasets[1].data = paddedMinData;
      
      // Add forecast as a new dataset
      if (forecastMax && forecastMax.length > 0) {
        datasets.push({
          label: 'Forecast Max',
          data: [...Array(maxData.length).fill(null), ...forecastMax],
          borderColor: '#dc2626',
          backgroundColor: 'rgba(220, 38, 38, 0.1)',
          borderDash: [5, 5],
          tension: 0.4,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 7,
          pointBackgroundColor: '#dc2626',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        });
      }

      // Add forecast min as a new dataset
      if (forecastMin && forecastMin.length > 0) {
        datasets.push({
          label: 'Forecast Min',
          data: [...Array(minData.length).fill(null), ...forecastMin],
          borderColor: '#1e40af',
          backgroundColor: 'rgba(30, 64, 175, 0.1)',
          borderDash: [5, 5],
          tension: 0.4,
          fill: true,
          pointRadius: 0,
          pointHoverRadius: 7,
          pointBackgroundColor: '#1e40af',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        });
      }
    }
    
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: extendedLabels,
        datasets: datasets
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

  $: if ((labels && labels.length && canvasEl) || forecastMax || forecastMin) {
    createChart();
  }

  onDestroy(() => { if (chart) chart.destroy(); });
</script>

<div style="width:100%; height:400px;">
  <canvas bind:this={canvasEl}></canvas>
</div>
