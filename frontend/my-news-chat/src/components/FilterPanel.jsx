import PropTypes from "prop-types";

function FilterPanel({
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
  selectedCategory,
  onCategoryChange,
  availableCategories,
  selectedSource,
  onSourceChange,
  availableSources,
}) {
  return (
    <div className="intel-card grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-4">
      <div>
        <div className="intel-kicker mb-2">From Date</div>
        <input
          type="date"
          value={dateFrom || ""}
          onChange={(e) => onDateFromChange(e.target.value || null)}
          className="intel-select"
        />
      </div>

      <div>
        <div className="intel-kicker mb-2">To Date</div>
        <input
          type="date"
          value={dateTo || ""}
          onChange={(e) => onDateToChange(e.target.value || null)}
          className="intel-select"
        />
      </div>

      <div>
        <div className="intel-kicker mb-2">Topic</div>
        <select
          value={selectedCategory || ""}
          onChange={(e) => onCategoryChange(e.target.value || null)}
          className="intel-select"
        >
          <option value="">All</option>
          {availableCategories?.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div>
        <div className="intel-kicker mb-2">Source</div>
        <select
          value={selectedSource || ""}
          onChange={(e) => onSourceChange(e.target.value || null)}
          className="intel-select"
        >
          <option value="">All</option>
          {availableSources?.map((src) => (
            <option key={src} value={src}>
              {src.substring(0, 12)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

FilterPanel.propTypes = {
  dateFrom: PropTypes.string,
  onDateFromChange: PropTypes.func.isRequired,
  dateTo: PropTypes.string,
  onDateToChange: PropTypes.func.isRequired,
  selectedCategory: PropTypes.string,
  onCategoryChange: PropTypes.func.isRequired,
  availableCategories: PropTypes.arrayOf(PropTypes.string),
  selectedSource: PropTypes.string,
  onSourceChange: PropTypes.func.isRequired,
  availableSources: PropTypes.arrayOf(PropTypes.string),
};

export default FilterPanel;
