import { formatMessageDateTime } from '../utils/dateTime';

const ExpandedMessageModal = ({ message, onClose, onDelete }) => {
  const messageTimeStyle = {
    fontSize: '11px',
    opacity: 0.6,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    fontWeight: 'bold',
  };

  const messageTextStyle = {
    fontSize: '14px',
    lineHeight: '1.8',
  };

  const expandedMessageStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  };

  const expandedContentStyle = {
    backgroundColor: '#fff',
    border: '4px solid #000',
    padding: '24px',
    borderRadius: '4px',
    maxWidth: '700px',
    maxHeight: '80vh',
    overflowY: 'auto',
    boxShadow: '8px 8px 0px #000',
    position: 'relative',
  };

  const closeButtonStyle = {
    position: 'absolute',
    top: '12px',
    right: '12px',
    width: '32px',
    height: '32px',
    border: '2px solid #000',
    backgroundColor: '#fff',
    fontWeight: 'bold',
    fontSize: '18px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  };

  const deleteButtonStyle = {
    marginTop: '16px',
    padding: '12px',
    backgroundColor: '#ff6b6b',
    color: '#fff',
    border: 'none',
    fontWeight: 'bold',
    cursor: 'pointer',
    width: '100%',
    borderRadius: '4px',
    fontSize: '12px',
  };

  if (!message) return null;

  return (
    <div style={expandedMessageStyle} onClick={onClose}>
      <div style={expandedContentStyle} onClick={(e) => e.stopPropagation()}>
        <button style={closeButtonStyle} onClick={onClose}>
          X
        </button>
        <div style={{ marginTop: '16px' }}>
          <div style={messageTimeStyle}>
            {formatMessageDateTime(message.created_at)} - {message.role === 'user' ? 'YOUR QUESTION' : 'RESPONSE'}
          </div>
          <div style={{ ...messageTextStyle, marginTop: '16px' }}>
            {message.text}
          </div>
          {message.sources && message.sources.length > 0 && (
            <div style={{ marginTop: '16px' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>SOURCES:</div>
              {message.sources.map((source, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '8px',
                    backgroundColor: '#eee',
                    marginBottom: '8px',
                    borderRadius: '4px',
                    fontSize: '13px',
                  }}
                >
                  {source.title || source.category}
                </div>
              ))}
            </div>
          )}
          <button
            style={deleteButtonStyle}
            onClick={() => onDelete(message.id)}
          >
            DELETE MESSAGE
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExpandedMessageModal;
