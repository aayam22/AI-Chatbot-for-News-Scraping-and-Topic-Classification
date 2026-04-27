import LoadingDots from './LoadingDots';
import SourceCard from './SourceCard';
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
        <div key={`line-${index}`} className="grid grid-cols-[14px_1fr] gap-3">
          <span className="font-black">-</span>
          <span>{renderInlineSegments(line.slice(2))}</span>
        </div>
      );
    }

    return (
      <p key={`line-${index}`} className="m-0">
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
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`w-full max-w-[840px] rounded-[1.5rem] px-5 py-5 sm:px-6 ${
          isUser
            ? 'border-2 border-black bg-[linear-gradient(135deg,#111,#242424)] text-white shadow-[0_18px_40px_rgba(0,0,0,0.16)]'
            : 'border border-black/12 bg-[linear-gradient(135deg,rgba(255,255,255,0.98),rgba(246,246,246,0.92))] text-zinc-950 shadow-[0_18px_40px_rgba(15,23,42,0.08)]'
        }`}
      >
        <div
          className={`mb-3 flex flex-wrap items-center justify-between gap-3 text-[11px] font-extrabold uppercase tracking-[0.14em] ${
            isUser ? 'text-white/70' : 'text-zinc-500'
          }`}
        >
          <span className="inline-flex items-center gap-2">
            <span>{role === 'user' ? 'User Query' : 'News Brief'}</span>
          </span>
          <span>{time || 'Live'}</span>
        </div>

        <div className="grid gap-3 text-[15px] leading-7">
          {loading ? <LoadingDots text={UI_MESSAGES.GENERATING_ANSWER} /> : renderFormattedText(text)}
        </div>

        {sources?.length > 0 && (
          <div className="mt-5 grid gap-3 border-t border-zinc-400/25 pt-4">
            <div className={`text-xs font-bold uppercase tracking-[0.12em] ${isUser ? 'text-white/70' : 'text-zinc-500'}`}>
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
