const ArchiveControls = ({ searchTerm, onSearchChange, activeFilter, onFilterChange }) => {
  const controlsStyle = {
    display: 'flex',
    gap: '12px',
    padding: '16px 24px',
    borderBottom: '2px solid #000',
    backgroundColor: '#fff',
    alignItems: 'center',
    flexWrap: 'wrap',
  };

  const searchInputStyle = {
    flex: 1,
    minWidth: '200px',
    padding: '12px',
    border: '2px solid #000',
    fontFamily: '"Space Grotesk", sans-serif',
    fontWeight: 'bold',
    fontSize: '14px',
  };

  const filterButtonStyle = (isActive) => ({
    padding: '12px 16px',
    border: `2px solid #000`,
    backgroundColor: isActive ? '#000' : '#fff',
    color: isActive ? '#fff' : '#000',
    fontWeight: 'bold',
    fontSize: '12px',
    cursor: 'pointer',
    textTransform: 'uppercase',
    transition: 'all 0.2s',
    boxShadow: isActive ? 'none' : '2px 2px 0px #000',
  });

  return (
    <div style={controlsStyle}>
      <input
        type="text"
        placeholder="Search conversations..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        style={searchInputStyle}
      />
      <button
        onClick={() => onFilterChange('all')}
        style={filterButtonStyle(activeFilter === 'all')}
      >
        All
      </button>
      <button
        onClick={() => onFilterChange('user')}
        style={filterButtonStyle(activeFilter === 'user')}
      >
        Your Q's
      </button>
      <button
        onClick={() => onFilterChange('assistant')}
        style={filterButtonStyle(activeFilter === 'assistant')}
      >
        Answers
      </button>
    </div>
  );
};

export default ArchiveControls;
