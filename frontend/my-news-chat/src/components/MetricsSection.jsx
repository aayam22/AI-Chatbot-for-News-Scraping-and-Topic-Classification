import PropTypes from 'prop-types';
import MetricCard from './MetricCard';

/**
 * MetricsSection - Displays key metrics in a grid
 */
function MetricsSection({ analysisData, categoryDist, sourceDist }) {
  const metricsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
    gap: '12px',
  };

  return (
    <div style={metricsGridStyle}>
      <MetricCard
        label="Total Articles"
        value={(analysisData?.total_articles || 0).toLocaleString()}
        icon="📰"
      />
      <MetricCard
        label="Predicted Topics"
        value={Object.keys(categoryDist).length || 0}
        icon="🎯"
      />
      <MetricCard
        label="Sources"
        value={Object.keys(sourceDist).length || 0}
        icon="📡"
      />
      <MetricCard
        label="Date Range"
        value={`${analysisData?.date_range?.from?.substring(5) || 'N/A'} - ${
          analysisData?.date_range?.to?.substring(5) || 'N/A'
        }`}
        icon="📅"
      />
    </div>
  );
}

MetricsSection.propTypes = {
  analysisData: PropTypes.shape({
    total_articles: PropTypes.number,
    date_range: PropTypes.shape({
      from: PropTypes.string,
      to: PropTypes.string,
    }),
  }),
  categoryDist: PropTypes.object.isRequired,
  sourceDist: PropTypes.object.isRequired,
};

export default MetricsSection;
