import { useState } from 'react';
import { STYLES } from '../constants/styles';
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
    <div style={STYLES.INPUT_CONTAINER}>
      <div style={STYLES.INPUT_FIELD_WRAP}>
        <div style={STYLES.INPUT_LABEL_ROW}>
          <label htmlFor="chat-input" style={STYLES.INPUT_LABEL}>
            Query Console
          </label>
          <span style={STYLES.INPUT_HINT}>Press Enter to send</span>
        </div>

        <textarea
          id="chat-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={PLACEHOLDERS.CHAT_INPUT}
          disabled={disabled}
          style={STYLES.INPUT_FIELD}
          rows={1}
        />
      </div>

      <div style={STYLES.BUTTON_GROUP}>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled || !question.trim()}
          style={STYLES.BUTTON('primary')}
        >
          {BUTTON_LABELS.SEND}
        </button>

        <button
          type="button"
          onClick={onClear}
          disabled={disabled}
          style={STYLES.BUTTON('secondary')}
        >
          {BUTTON_LABELS.CLEAR}
        </button>
      </div>
    </div>
  );
}
