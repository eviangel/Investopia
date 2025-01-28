import React from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import './PortfolioChart.css';

// Register required Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const PortfolioChart = () => {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Portfolio Value',
        data: [12000, 15000, 17000, 20000, 25000, 30000],
        borderColor: '#1abc9c',
        backgroundColor: 'rgba(26, 188, 156, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: '#ffffff',
        },
      },
    },
    scales: {
      x: {
        type: 'category', // Explicitly set the scale type
        grid: {
          display: false,
        },
        ticks: {
          color: '#ffffff',
        },
      },
      y: {
        grid: {
          color: '#444',
        },
        ticks: {
          color: '#ffffff',
        },
      },
    },
  };

  return (
    <div className="portfolio-chart" style={{ height: '300px' }}>
      <h3>Portfolio Overview</h3>
      <Line data={data} options={options} />
    </div>
  );
};

export default PortfolioChart;
