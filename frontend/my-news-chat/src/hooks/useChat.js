import { useCallback } from 'react';
import { askQuestion, formatAssistantMessage } from '../services/chatService';
import { UI_MESSAGES } from '../constants/messages';

/**
 * Custom hook for chat operations (send question, clear chat)
 * Handles API calls and message state updates
 */
export const useChat = (setMessages, clearVisibleMessages, token, refreshMessages) => {
  /**
   * Generate unique message ID
   */
  const generateMessageId = useCallback(
    () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    []
  );

  /**
   * Send a question and handle the response
   */
  const sendQuestion = useCallback(
    async (question) => {
      if (!question.trim() || !token) return;

      const userMsg = {
        id: generateMessageId(),
        role: 'user',
        text: question,
        time: new Date().toLocaleTimeString()
      };

      const loadingMsgId = generateMessageId();

      // Add user + loading message
      setMessages(prev => [
        ...prev,
        userMsg,
        {
          id: loadingMsgId,
          role: 'assistant',
          text: UI_MESSAGES.GENERATING_ANSWER,
          loading: true
        }
      ]);

      // Call API
      const result = await askQuestion(question, token);

      if (result.success) {
        const assistantMsg = formatAssistantMessage(result.data, loadingMsgId);

        setMessages(prev =>
          prev.map(msg => (msg.id === loadingMsgId ? assistantMsg : msg))
        );

        if (refreshMessages) {
          await refreshMessages();
        }
      } else {
        // Show error message
        setMessages(prev =>
          prev.map(msg =>
            msg.id === loadingMsgId
              ? {
                  ...msg,
                  text: `${UI_MESSAGES.ERROR_PREFIX}${result.error}`,
                  loading: false
                }
              : msg
          )
        );
      }
    },
    [token, setMessages, generateMessageId, refreshMessages]
  );

  /**
   * Clear only the current in-page chat view.
   * This should not remove archived server history.
   */
  const clearChat = useCallback(async () => {
    clearVisibleMessages();
  }, [clearVisibleMessages]);

  return { sendQuestion, clearChat, generateMessageId };
};

export default useChat;
