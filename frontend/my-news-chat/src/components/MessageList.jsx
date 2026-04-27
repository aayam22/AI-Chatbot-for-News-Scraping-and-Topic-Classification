import ChatMessage from './ChatMessage';
import useAutoScroll from '../hooks/useAutoScroll';
import { UI_MESSAGES } from '../constants/messages';

/**
 * MessageList Component - Displays all chat messages
 * Includes auto-scroll and empty state
 */
export default function MessageList({ messages, onImageClick }) {
  const lastMessageRef = useAutoScroll(messages);

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-5">
        {messages.length === 0 && (
          <div className="rounded-[1.5rem] border-2 border-dashed border-black/20 bg-[linear-gradient(135deg,rgba(255,255,255,0.98),rgba(245,245,245,0.92))] p-7">
            <h2 className="text-xl font-black uppercase tracking-[-0.04em] text-zinc-950">
              Ready For the Next Brief
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-zinc-600">{UI_MESSAGES.WELCOME}</p>
            <div className="mt-5 flex flex-wrap gap-3">
              <span className="intel-chip">Latest headlines</span>
              <span className="intel-chip">Topic summaries</span>
              <span className="intel-chip">Source-backed answers</span>
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
