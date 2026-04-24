import MessageItem from './MessageItem';

const MessageGroup = ({ date, messages, onExpandMessage }) => {
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
      {messages.map((msg) => (
        <MessageItem key={msg.id} msg={msg} onExpand={onExpandMessage} />
      ))}
    </div>
  );
};

export default MessageGroup;
