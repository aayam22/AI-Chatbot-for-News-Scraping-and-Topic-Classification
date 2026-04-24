const ArchiveControls = ({ searchTerm, onSearchChange }) => {
  const controlsStyle = {
    display: 'flex',
    gap: '12px',
    padding: '16px 24px',
    borderBottom: '2px solid #000',
    backgroundColor: '#fff',
    alignItems: 'center',
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

  return (
    <div style={controlsStyle}>
      <input
        type="text"
        placeholder="Search conversations..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        style={searchInputStyle}
      />
    </div>
  );
};

export default ArchiveControls;
