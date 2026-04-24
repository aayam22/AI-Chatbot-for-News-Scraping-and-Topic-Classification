import ConversationItem from './ConversationItem';

const MessageGroup = ({ date, conversations, onExpandMessage }) => {
  const dateGroupStyle = {
    marginBottom: '32px',
  };

  const dateHeaderStyle = {
    fontSize: '14px',
    fontWeight: '900',
    color: '#000',
    marginBottom: '16px',
    paddingBottom: '8px',
    borderBottom: '2px solid #000',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  };

  return (
    <div style={dateGroupStyle}>
      <div style={dateHeaderStyle}>{date}</div>
      {conversations.map((conversation) => (
        <ConversationItem
          key={conversation.id}
          turn={conversation}
          onExpand={onExpandMessage}
        />
      ))}
    </div>
  );
};

export default MessageGroup;
