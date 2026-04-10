import PropTypes from 'prop-types';

/**
 * FilterPanel - Display filter controls for analysis data
 */
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
  const filterContainerStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: '12px',
    padding: '16px',
    backgroundColor: '#fff',
    border: '2px solid #000',
    borderRadius: '0px',
  };

  const filterGroupStyle = {
    display: 'flex',
    flexDirection: 'column',
  };

  const filterLabelStyle = {
    fontSize: '10px',
    fontWeight: '900',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginBottom: '6px',
    color: '#000',
  };

  const filterInputStyle = {
    padding: '8px 12px',
    border: '2px solid #000',
    backgroundColor: '#fff',
    fontFamily: '"Space Grotesk", sans-serif',
    fontSize: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  };

  return (
    <div style={filterContainerStyle}>
      <div style={filterGroupStyle}>
        <div style={filterLabelStyle}>From Date</div>
        <input
          type="date"
          value={dateFrom || ''}
          onChange={(e) => onDateFromChange(e.target.value || null)}
          style={filterInputStyle}
        />
      </div>

      <div style={filterGroupStyle}>
        <div style={filterLabelStyle}>To Date</div>
        <input
          type="date"
          value={dateTo || ''}
          onChange={(e) => onDateToChange(e.target.value || null)}
          style={filterInputStyle}
        />
      </div>

      <div style={filterGroupStyle}>
        <div style={filterLabelStyle}>Topic</div>
        <select
          value={selectedCategory || ''}
          onChange={(e) => onCategoryChange(e.target.value || null)}
          style={filterInputStyle}
        >
          <option value="">All</option>
          {availableCategories?.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div style={filterGroupStyle}>
        <div style={filterLabelStyle}>Source</div>
        <select
          value={selectedSource || ''}
          onChange={(e) => onSourceChange(e.target.value || null)}
          style={filterInputStyle}
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
