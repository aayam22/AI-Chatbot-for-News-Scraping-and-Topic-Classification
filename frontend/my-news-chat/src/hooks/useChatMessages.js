import { useState, useEffect, useCallback } from 'react';
import { STORAGE_KEYS } from '../constants/config';

/**
 * Custom hook for managing chat messages with localStorage persistence
 */
export const useChatMessages = () => {
  const [messages, setMessages] = useState([]);

  // Load messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem(STORAGE_KEYS.CHAT_MESSAGES);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (error) {
        console.error('Error loading messages from localStorage:', error);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.CHAT_MESSAGES, JSON.stringify(messages));
  }, [messages]);

  // Clear messages and localStorage
  const clearAllMessages = useCallback(() => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
  }, []);

  return { messages, setMessages, clearAllMessages };
};

export default useChatMessages;
