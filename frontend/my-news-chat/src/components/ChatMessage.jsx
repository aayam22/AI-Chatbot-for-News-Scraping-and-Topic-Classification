import LoadingDots from './LoadingDots';
import SourceCard from './SourceCard';
import { STYLES } from '../constants/styles';
import { UI_MESSAGES } from '../constants/messages';

/**
 * ChatMessage Component - Displays a single chat message with sources
 * Handles both user and assistant messages
 */
export default function ChatMessage({ message, onImageClick }) {
  const { role, text, loading, sources } = message;

  return (
    <div style={STYLES.MESSAGE_WRAPPER(role)}>
      <div style={STYLES.MESSAGE_BOX(role)}>
        {/* Message Text */}
        <div style={{ marginBottom: sources?.length ? '10px' : 0 }}>
          {loading ? <LoadingDots text={UI_MESSAGES.GENERATING_ANSWER} /> : text}
        </div>

        {/* Sources */}
        {sources?.length > 0 && (
          <>
            <div style={STYLES.SOURCES_HEADER}>
              {UI_MESSAGES.SOURCES_COUNT(sources.length)}
            </div>

            {sources.slice(0, 3).map((source, index) => (
              <SourceCard
                key={index}
                source={source}
                onImageClick={onImageClick}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
