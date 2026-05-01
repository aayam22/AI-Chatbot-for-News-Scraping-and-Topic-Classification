import { useState, useEffect, useCallback } from 'react';
import { STORAGE_KEYS } from '../constants/config';
import { getChatHistory } from '../services/chatHistoryService';
import { formatMessageTime, normalizeServerTimestamp } from '../utils/dateTime';

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
    time: formatMessageTime(message.created_at)
  }));
}

function getInitialClearedAt() {
  return localStorage.getItem(STORAGE_KEYS.CHAT_PAGE_CLEARED_AT);
}

function isMessageVisible(message, clearedAt) {
  if (!clearedAt || !message.created_at) {
    return true;
  }

  const clearedAtTime = normalizeServerTimestamp(clearedAt)?.getTime();
  const messageTime = normalizeServerTimestamp(message.created_at)?.getTime();

  if (clearedAtTime == null || messageTime == null) {
    return true;
  }

  return messageTime >= clearedAtTime;
}

function filterVisibleMessages(messages, clearedAt) {
  return messages.filter((message) => isMessageVisible(message, clearedAt));
}

/**
 * Custom hook for managing chat messages with localStorage persistence
 */
export const useChatMessages = (token) => {
  const [messages, setMessages] = useState(getInitialMessages);
  const [chatPageClearedAt, setChatPageClearedAt] = useState(getInitialClearedAt);

  const refreshMessages = useCallback(async () => {
    if (!token) {
      setMessages([]);
      return { success: true, data: [] };
    }

    const result = await getChatHistory(token, 1000, 0);

    if (result.success) {
      const normalizedMessages = normalizeServerMessages(result.data.messages || []);
      const visibleMessages = filterVisibleMessages(normalizedMessages, chatPageClearedAt);
      setMessages(visibleMessages);
      return { success: true, data: visibleMessages };
    }

    console.error('Error loading chat history from server:', result.error);
    return { success: false, error: result.error };
  }, [token, chatPageClearedAt]);

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
        const normalizedMessages = normalizeServerMessages(result.data.messages || []);
        setMessages(filterVisibleMessages(normalizedMessages, chatPageClearedAt));
      } else {
        console.error('Error loading chat history from server:', result.error);
      }
    };

    fetchInitialMessages();

    return () => {
      isActive = false;
    };
  }, [token, chatPageClearedAt]);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.CHAT_MESSAGES, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (chatPageClearedAt) {
      localStorage.setItem(STORAGE_KEYS.CHAT_PAGE_CLEARED_AT, chatPageClearedAt);
    } else {
      localStorage.removeItem(STORAGE_KEYS.CHAT_PAGE_CLEARED_AT);
    }
  }, [chatPageClearedAt]);

  const clearVisibleMessages = useCallback(() => {
    setChatPageClearedAt(new Date().toISOString());
    setMessages([]);
  }, []);

  // Clear messages and localStorage
  const clearAllMessages = useCallback(() => {
    setMessages([]);
    setChatPageClearedAt(null);
    localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
    localStorage.removeItem(STORAGE_KEYS.CHAT_PAGE_CLEARED_AT);
  }, []);

  const removeMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((message) => message.id !== messageId));
  }, []);

  return {
    messages,
    setMessages,
    clearVisibleMessages,
    clearAllMessages,
    refreshMessages,
    removeMessage
  };
};

export default useChatMessages;
