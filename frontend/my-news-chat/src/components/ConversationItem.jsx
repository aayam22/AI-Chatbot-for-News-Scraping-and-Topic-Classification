import { formatMessageTime } from '../utils/dateTime';

const ConversationItem = ({ turn, onExpand }) => {
  const containerStyle = {
    marginBottom: '18px',
    border: '2px solid #000',
    borderRadius: '6px',
    overflow: 'hidden',
    backgroundColor: '#fff',
    boxShadow: '2px 2px 0px rgba(0,0,0,0.08)',
    cursor: 'pointer',
  };

  const sectionStyle = (isUser) => ({
    padding: '16px 18px',
    backgroundColor: isUser ? '#000' : '#f2f2f2',
    color: isUser ? '#fff' : '#000',
    borderTop: isUser ? 'none' : '2px solid #000',
  });

  const metaStyle = (isUser) => ({
    fontSize: '11px',
    opacity: isUser ? 0.7 : 0.6,
    marginBottom: '10px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    fontWeight: 'bold',
  });

  const textStyle = {
    fontSize: '14px',
    lineHeight: '1.6',
    wordBreak: 'break-word',
  };

  const sourceStyle = {
    marginTop: '8px',
    fontSize: '11px',
    opacity: 0.7
  };

  const previewText = (text) => {
    if (!text) {
      return '';
    }

    return text.length > 180 ? `${text.substring(0, 180)}...` : text;
  };

  const expandableMessage = turn.assistant ?? turn.user;

  return (
    <div
      style={containerStyle}
      onClick={() => expandableMessage && onExpand(expandableMessage)}
    >
      {turn.user && (
        <div style={sectionStyle(true)}>
          <div style={metaStyle(true)}>
            {formatMessageTime(turn.user.created_at)} - YOU
          </div>
          <div style={textStyle}>{previewText(turn.user.text)}</div>
        </div>
      )}

      {turn.assistant && (
        <div style={sectionStyle(false)}>
          <div style={metaStyle(false)}>
            {formatMessageTime(turn.assistant.created_at)} - ASSISTANT
          </div>
          <div style={textStyle}>{previewText(turn.assistant.text)}</div>
          {turn.assistant.sources && turn.assistant.sources.length > 0 && (
            <div style={sourceStyle}>
              {turn.assistant.sources.length} source{turn.assistant.sources.length > 1 ? 's' : ''}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConversationItem;
