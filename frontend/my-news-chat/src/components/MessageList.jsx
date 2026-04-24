import ChatMessage from './ChatMessage';
import useAutoScroll from '../hooks/useAutoScroll';
import { STYLES } from '../constants/styles';
import { UI_MESSAGES } from '../constants/messages';

/**
 * MessageList Component - Displays all chat messages
 * Includes auto-scroll and empty state
 */
export default function MessageList({ messages, onImageClick }) {
  const lastMessageRef = useAutoScroll(messages);

  return (
    <div style={STYLES.MESSAGES_AREA}>
      <div style={STYLES.MESSAGES_INNER}>
        {messages.length === 0 && (
          <div style={STYLES.EMPTY_STATE}>
            <h2 style={STYLES.EMPTY_STATE_TITLE}>Ready For the Next Brief</h2>
            <p style={STYLES.EMPTY_STATE_TEXT}>{UI_MESSAGES.WELCOME}</p>
            <div style={STYLES.EMPTY_STATE_TIPS}>
              <span style={STYLES.EMPTY_STATE_TIP}>Latest headlines</span>
              <span style={STYLES.EMPTY_STATE_TIP}>Topic summaries</span>
              <span style={STYLES.EMPTY_STATE_TIP}>Source-backed answers</span>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={message.id}
            ref={index === messages.length - 1 ? lastMessageRef : null}
          >
            <ChatMessage
              message={message}
              onImageClick={onImageClick}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
