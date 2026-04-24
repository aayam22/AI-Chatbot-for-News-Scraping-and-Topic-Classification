const MessageItem = ({ msg, onExpand }) => {
  const messageItemStyle = (isUser) => ({
    marginBottom: '16px',
    padding: '16px',
    backgroundColor: isUser ? '#000' : '#eee',
    color: isUser ? '#fff' : '#000',
    border: '2px solid #000',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '2px 2px 0px rgba(0,0,0,0.1)',
    '&:hover': {
      boxShadow: '4px 4px 0px #000',
    },
  });

  const messageTimeStyle = {
    fontSize: '11px',
    opacity: 0.6,
    marginBottom: '8px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    fontWeight: 'bold',
  };

  const messageTextStyle = {
    fontSize: '14px',
    lineHeight: '1.6',
    wordBreak: 'break-word',
  };

  return (
    <div
      style={messageItemStyle(msg.role === 'user')}
      onClick={() => onExpand(msg)}
    >
      <div style={messageTimeStyle}>
        {new Date(msg.created_at).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })} • {msg.role === 'user' ? 'YOU' : 'ASSISTANT'}
      </div>
      <div style={messageTextStyle}>
        {msg.text.length > 150 ? `${msg.text.substring(0, 150)}...` : msg.text}
      </div>
      {msg.sources && msg.sources.length > 0 && (
        <div style={{ marginTop: '8px', fontSize: '11px', opacity: 0.7 }}>
          📎 {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default MessageItem;
