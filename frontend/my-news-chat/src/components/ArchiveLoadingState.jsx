const ArchiveLoadingState = () => {
  const archiveContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#fff',
    fontFamily: '"Space Grotesk", sans-serif',
  };

  const headerStyle = {
    borderBottom: '4px solid #000',
    padding: '24px',
    backgroundColor: '#eee',
  };

  const headerTitleStyle = {
    fontSize: '28px',
    fontWeight: '900',
    margin: '0 0 12px 0',
    letterSpacing: '-1px',
  };

  return (
    <div style={archiveContainerStyle}>
      <div style={headerStyle}>
        <h1 style={headerTitleStyle}>ARCHIVE</h1>
        <p style={{ margin: '0', fontSize: '14px', opacity: 0.7 }}>Loading chat history...</p>
      </div>
    </div>
  );
};

export default ArchiveLoadingState;
