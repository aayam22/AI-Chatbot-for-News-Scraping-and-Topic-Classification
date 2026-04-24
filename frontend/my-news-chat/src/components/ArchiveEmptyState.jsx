const ArchiveEmptyState = ({ error, searchTerm }) => {
  const emptyStateStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    opacity: 0.6,
  };

  if (error) {
    return (
      <div style={{ ...emptyStateStyle, color: '#ff6b6b' }}>
        <p style={{ fontSize: '16px', fontWeight: 'bold' }}>{error}</p>
      </div>
    );
  }

  return (
    <div style={emptyStateStyle}>
      <p style={{ fontSize: '16px', fontWeight: 'bold' }}>
        {searchTerm ? 'No matching conversations' : 'No chat history yet'}
      </p>
    </div>
  );
};

export default ArchiveEmptyState;
