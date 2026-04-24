import LoadingDots from './LoadingDots';
import SourceCard from './SourceCard';
import { STYLES } from '../constants/styles';
import { UI_MESSAGES } from '../constants/messages';

function renderInlineSegments(text) {
  return text.split(/(\*\*.*?\*\*)/g).filter(Boolean).map((segment, index) => {
    if (segment.startsWith('**') && segment.endsWith('**')) {
      return <strong key={`${segment}-${index}`}>{segment.slice(2, -2)}</strong>;
    }

    return <span key={`${segment}-${index}`}>{segment}</span>;
  });
}

function renderFormattedText(text) {
  const normalized = String(text ?? '')
    .replace(/\r\n/g, '\n')
    .replace(/\s\*\s+/g, '\n- ')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  return normalized.map((line, index) => {
    if (line.startsWith('- ')) {
      return (
        <div key={`line-${index}`} style={STYLES.MESSAGE_BULLET}>
          <span style={STYLES.MESSAGE_BULLET_DOT}>-</span>
          <span>{renderInlineSegments(line.slice(2))}</span>
        </div>
      );
    }

    return (
      <p key={`line-${index}`} style={STYLES.MESSAGE_PARAGRAPH}>
        {renderInlineSegments(line)}
      </p>
    );
  });
}

/**
 * ChatMessage Component - Displays a single chat message with sources
 * Handles both user and assistant messages
 */
export default function ChatMessage({ message, onImageClick }) {
  const { role, text, loading, sources, time } = message;

  return (
    <div style={STYLES.MESSAGE_WRAPPER(role)}>
      <div style={STYLES.MESSAGE_BOX(role)}>
        <div style={STYLES.MESSAGE_META(role)}>
          <span style={STYLES.MESSAGE_ROLE}>
            <span>{role === 'user' ? 'User Query' : 'News Brief'}</span>
          </span>
          <span>{time || 'Live'}</span>
        </div>

        <div style={STYLES.MESSAGE_TEXT}>
          {loading ? <LoadingDots text={UI_MESSAGES.GENERATING_ANSWER} /> : renderFormattedText(text)}
        </div>

        {sources?.length > 0 && (
          <div style={STYLES.SOURCES_SECTION}>
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
          </div>
        )}
      </div>
    </div>
  );
}
