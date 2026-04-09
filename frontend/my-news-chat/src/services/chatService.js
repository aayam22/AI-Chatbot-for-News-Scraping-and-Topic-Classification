import axios from 'axios';
import { API_CONFIG } from '../constants/config';
import { UI_MESSAGES } from '../constants/messages';

const api = axios.create({
  baseURL: API_CONFIG.BACKEND_URL,
  timeout: API_CONFIG.TIMEOUT
});

/**
 * Send a question to the chat API
 * @param {string} question - The user's question
 * @param {string} token - Authorization token
 * @returns {Promise} API response with answer and sources
 */
export const askQuestion = async (question, token) => {
  try {
    const response = await api.post(
      API_CONFIG.ENDPOINTS.ASK,
      { question },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Unknown error'
    };
  }
};

/**
 * Clear chat memory on backend
 * @param {string} token - Authorization token
 * @returns {Promise} Success status
 */
export const clearChatMemory = async (token) => {
  try {
    await api.post(
      API_CONFIG.ENDPOINTS.CLEAR_MEMORY,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return { success: true };
  } catch (error) {
    console.warn('Error clearing backend memory:', error.message);
    return { success: false, error: error.message };
  }
};

/**
 * Transform API response to standardized message format
 * @param {Object} data - API response data
 * @returns {Object} Formatted message object
 */
export const formatAssistantMessage = (data, messageId) => {
  return {
    id: messageId,
    role: 'assistant',
    text: typeof data.answer === 'string' ? data.answer : JSON.stringify(data.answer),
    sources: Array.isArray(data.sources)
      ? data.sources.map(s => ({
          category: s.category || UI_MESSAGES.DEFAULT_SOURCE_CATEGORY,
          title: s.title || UI_MESSAGES.DEFAULT_SOURCE_TITLE,
          image_url: s.image_url || null
        }))
      : [],
    time: new Date().toLocaleTimeString()
  };
};

export default { askQuestion, clearChatMemory, formatAssistantMessage };
