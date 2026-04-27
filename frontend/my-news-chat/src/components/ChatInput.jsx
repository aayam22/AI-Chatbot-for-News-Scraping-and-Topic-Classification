import { useState } from 'react';
import { BUTTON_LABELS, PLACEHOLDERS } from '../constants/messages';

/**
 * ChatInput Component - Input field and action buttons
 * Handles question submission and chat clearing
 */
export default function ChatInput({ onSend, onClear, disabled }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = () => {
    if (question.trim()) {
      onSend(question);
      setQuestion('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="intel-card flex flex-wrap items-end gap-3 p-3 sm:p-4">
      <div className="min-w-[16rem] flex-1">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
          <label htmlFor="chat-input" className="intel-kicker">
            Query Console
          </label>
          <span className="text-xs font-medium text-zinc-500">Press Enter to send</span>
        </div>

        <textarea
          id="chat-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={PLACEHOLDERS.CHAT_INPUT}
          disabled={disabled}
          className="intel-input min-h-[56px] resize-none rounded-[1.1rem]"
          rows={1}
        />
      </div>

      <div className="flex w-full flex-wrap gap-3 sm:w-auto">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || !question.trim()}
          className="intel-button min-w-[120px] flex-1 sm:flex-none"
        >
          {BUTTON_LABELS.SEND}
        </button>

        <button
          type="button"
          onClick={onClear}
          disabled={disabled}
          className="intel-button-secondary min-w-[120px] flex-1 sm:flex-none"
        >
          {BUTTON_LABELS.CLEAR}
        </button>
      </div>
    </div>
  );
}
