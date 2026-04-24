import { useState, useEffect, useCallback } from 'react';
import { STORAGE_KEYS } from '../constants/config';
import { getChatHistory } from '../services/chatHistoryService';

function getInitialMessages() {
  const savedMessages = localStorage.getItem(STORAGE_KEYS.CHAT_MESSAGES);

  if (!savedMessages) {
    return [];
  }

  try {
    return JSON.parse(savedMessages);
  } catch (error) {
    console.error('Error loading messages from localStorage:', error);
    return [];
  }
}

function normalizeServerMessages(messages) {
  return messages.map((message) => ({
    id: message.id,
    role: message.role,
    text: message.text,
    sources: Array.isArray(message.sources) ? message.sources : [],
    created_at: message.created_at,
    time: message.created_at
      ? new Date(message.created_at).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })
      : ''
  }));
}

/**
 * Custom hook for managing chat messages with localStorage persistence
 */
export const useChatMessages = (token) => {
  const [messages, setMessages] = useState(getInitialMessages);

  const refreshMessages = useCallback(async () => {
    if (!token) {
      setMessages([]);
      return { success: true, data: [] };
    }

    const result = await getChatHistory(token, 1000, 0);

    if (result.success) {
      const normalizedMessages = normalizeServerMessages(result.data.messages || []);
      setMessages(normalizedMessages);
      return { success: true, data: normalizedMessages };
    }

    console.error('Error loading chat history from server:', result.error);
    return { success: false, error: result.error };
  }, [token]);

  useEffect(() => {
    let isActive = true;

    if (!token) {
      return () => {
        isActive = false;
      };
    }

    const fetchInitialMessages = async () => {
      const result = await getChatHistory(token, 1000, 0);

      if (!isActive) {
        return;
      }

      if (result.success) {
        setMessages(normalizeServerMessages(result.data.messages || []));
      } else {
        console.error('Error loading chat history from server:', result.error);
      }
    };

    fetchInitialMessages();

    return () => {
      isActive = false;
    };
  }, [token]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.CHAT_MESSAGES, JSON.stringify(messages));
  }, [messages]);

  // Clear messages and localStorage
  const clearAllMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
  }, []);

  const removeMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((message) => message.id !== messageId));
  }, []);

  return { messages, setMessages, clearAllMessages, refreshMessages, removeMessage };
};

export default useChatMessages;
