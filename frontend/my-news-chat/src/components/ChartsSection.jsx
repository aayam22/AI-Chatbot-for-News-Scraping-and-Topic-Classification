import PropTypes from 'prop-types';
import { useMemo } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

/**
 * ChartsSection - Displays analytics charts
 * Uses useMemo to optimize chart data recalculation
 */
function ChartsSection({ analysisData, chartOptions }) {
  const timeSeriesData = analysisData?.time_series || {};
  const topCategories = analysisData?.top_categories || [];
  const topSources = analysisData?.top_sources || [];

  // Memoize chart data to prevent unnecessary recalculations
  const lineChartData = useMemo(() => {
    const timeSeriesDates = Object.keys(timeSeriesData);
    const timeSeriesCounts = Object.values(timeSeriesData);

    return {
      labels: timeSeriesDates,
      datasets: [
        {
          label: 'Articles Over Time',
          data: timeSeriesCounts,
          borderColor: '#000',
          backgroundColor: 'rgba(0, 0, 0, 0.05)',
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#000',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    };
  }, [timeSeriesData]);

  const categoryChartData = useMemo(() => ({
    labels: topCategories.map((c) => c.name),
    datasets: [
      {
        label: 'Articles by Predicted Topic',
        data: topCategories.map((c) => c.count),
        backgroundColor: [
          'rgba(0, 0, 0, 0.9)',
          'rgba(0, 0, 0, 0.75)',
          'rgba(0, 0, 0, 0.6)',
          'rgba(0, 0, 0, 0.45)',
          'rgba(0, 0, 0, 0.3)',
        ],
        borderColor: '#000',
        borderWidth: 2,
      },
    ],
  }), [topCategories]);

  const sourceChartData = useMemo(() => ({
    labels: topSources.slice(0, 5).map((s) => s.name),
    datasets: [
      {
        label: 'Top Sources',
        data: topSources.slice(0, 5).map((s) => s.count),
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        borderColor: '#000',
        borderWidth: 2,
      },
    ],
  }), [topSources]);

  const timeSeriesDates = Object.keys(timeSeriesData);
  const hasData = timeSeriesDates.length > 0 || topCategories.length > 0 || topSources.length > 0;

  const chartsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
    gap: '16px',
  };

  const chartCardStyle = {
    padding: '20px',
    backgroundColor: '#fff',
    border: '3px solid #000',
    boxShadow: '3px 3px 0px rgba(0, 0, 0, 0.1)',
  };

  const chartTitleStyle = {
    fontSize: '14px',
    fontWeight: '900',
    marginBottom: '16px',
    color: '#000',
    letterSpacing: '-0.5px',
    textTransform: 'uppercase',
    borderBottom: '2px solid #000',
    paddingBottom: '8px',
  };

  const noDataStyle = {
    gridColumn: '1 / -1',
    padding: '32px',
    textAlign: 'center',
    color: '#999',
    backgroundColor: '#fff',
    border: '2px solid #ddd',
    fontSize: '14px',
    fontWeight: '600',
  };

  return (
    <div style={chartsGridStyle}>
      {timeSeriesDates.length > 0 && (
        <div style={chartCardStyle}>
          <h3 style={chartTitleStyle}>📈 Articles Over Time</h3>
          <Line data={lineChartData} options={chartOptions} />
        </div>
      )}

      {topCategories.length > 0 && (
        <div style={chartCardStyle}>
          <h3 style={chartTitleStyle}>🎯 Top Predicted Topics</h3>
          <Doughnut
            data={categoryChartData}
            options={{
              ...chartOptions,
              plugins: {
                ...chartOptions.plugins,
                legend: { ...chartOptions.plugins.legend, position: 'bottom' },
              },
            }}
          />
        </div>
      )}

      {topSources.length > 0 && (
        <div style={chartCardStyle}>
          <h3 style={chartTitleStyle}>📡 Top News Sources</h3>
          <Bar data={sourceChartData} options={chartOptions} />
        </div>
      )}

      {!hasData && (
        <div style={noDataStyle}>
          ⚠️ No data available for the selected filters
        </div>
      )}
    </div>
  );
}

ChartsSection.propTypes = {
  analysisData: PropTypes.shape({
    time_series: PropTypes.object,
    top_categories: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string,
        count: PropTypes.number,
      })
    ),
    top_sources: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string,
        count: PropTypes.number,
      })
    ),
  }),
  chartOptions: PropTypes.object.isRequired,
};

export default ChartsSection;
