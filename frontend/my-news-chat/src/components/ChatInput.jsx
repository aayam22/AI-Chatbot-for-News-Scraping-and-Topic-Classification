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
      <input
        id="chat-input"
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={PLACEHOLDERS.CHAT_INPUT}
        disabled={disabled}
        style={STYLES.INPUT_FIELD}
      />

      <button
        onClick={handleSubmit}
        disabled={disabled}
        style={STYLES.BUTTON}
      >
        {BUTTON_LABELS.SEND}
      </button>

      <button
        onClick={onClear}
        disabled={disabled}
        style={STYLES.BUTTON}
      >
        {BUTTON_LABELS.CLEAR}
      </button>
    </div>
  );
}
