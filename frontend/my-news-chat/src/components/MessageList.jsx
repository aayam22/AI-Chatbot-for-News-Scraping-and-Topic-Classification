import ChatMessage from './ChatMessage';
import useAutoScroll from '../hooks/useAutoScroll';
import { STYLES } from '../constants/styles';
import { UI_MESSAGES } from '../constants/messages';

/**
 * MessageList Component - Displays all chat messages
 * Includes auto-scroll and empty state
 */
export default function MessageList({ messages, onImageClick }) {
  const endRef = useAutoScroll(messages);

  return (
    <div style={STYLES.MESSAGES_AREA}>
      {messages.length === 0 && (
        <div style={STYLES.EMPTY_STATE}>
          {UI_MESSAGES.WELCOME}
        </div>
      )}

      {messages.map(message => (
        <ChatMessage
          key={message.id}
          message={message}
          onImageClick={onImageClick}
        />
      ))}

      <div ref={endRef} />
    </div>
  );
}
