import PropTypes from "prop-types";
import MetricCard from "./MetricCard";

function MetricsSection({ analysisData, categoryDist, sourceDist }) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <MetricCard
        label="Total Articles"
        value={(analysisData?.total_articles || 0).toLocaleString()}
        icon="VOL"
      />
      <MetricCard
        label="Predicted Topics"
        value={Object.keys(categoryDist).length || 0}
        icon="TOP"
      />
      <MetricCard
        label="Sources"
        value={Object.keys(sourceDist).length || 0}
        icon="SRC"
      />
      <MetricCard
        label="Date Range"
        value={`${analysisData?.date_range?.from?.substring(5) || "N/A"} - ${
          analysisData?.date_range?.to?.substring(5) || "N/A"
        }`}
        icon="RNG"
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
