import { formatMessageDateShort } from '../utils/dateTime';

const ArchiveHeader = ({ stats }) => {
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

  const statsStyle = {
    display: 'flex',
    gap: '24px',
    marginTop: '12px',
    flexWrap: 'wrap',
  };

  const statItemStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
  };

  const statLabelStyle = {
    fontSize: '11px',
    fontWeight: 'bold',
    opacity: 0.6,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  };

  const statValueStyle = {
    fontSize: '20px',
    fontWeight: '900',
    marginTop: '4px',
  };

  return (
    <div style={headerStyle}>
      <h1 style={headerTitleStyle}>ARCHIVE</h1>
      {stats && (
        <div style={statsStyle}>
          <div style={statItemStyle}>
            <span style={statLabelStyle}>Total Messages</span>
            <span style={statValueStyle}>{stats.total_messages}</span>
          </div>
          <div style={statItemStyle}>
            <span style={statLabelStyle}>Your Questions</span>
            <span style={statValueStyle}>{stats.user_messages}</span>
          </div>
          <div style={statItemStyle}>
            <span style={statLabelStyle}>Responses</span>
            <span style={statValueStyle}>{stats.assistant_messages}</span>
          </div>
          {stats.first_message && (
            <div style={statItemStyle}>
              <span style={statLabelStyle}>Since</span>
              <span style={statValueStyle}>
                {formatMessageDateShort(stats.first_message)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ArchiveHeader;
