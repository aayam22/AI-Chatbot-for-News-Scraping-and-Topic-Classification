import axios from 'axios';
import { API_CONFIG } from '../constants/config';

const api = axios.create({
  baseURL: API_CONFIG.BACKEND_URL,
  timeout: API_CONFIG.TIMEOUT
});

/**
 * Get all chat messages for the user
 * @param {string} token - Authorization token
 * @param {number} limit - Max messages to return
 * @param {number} offset - Pagination offset
 * @returns {Promise} API response with chat history
 */
export const getChatHistory = async (token, limit = 100, offset = 0) => {
  try {
    const response = await api.get(
      `/chat-history?limit=${limit}&offset=${offset}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to fetch chat history'
    };
  }
};

/**
 * Get chat statistics for the user
 * @param {string} token - Authorization token
 * @returns {Promise} API response with statistics
 */
export const getChatStats = async (token) => {
  try {
    const response = await api.get(
      `/chat-history/stats`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to fetch chat statistics'
    };
  }
};

/**
 * Delete a specific chat message
 * @param {number} messageId - ID of message to delete
 * @param {string} token - Authorization token
 * @returns {Promise} Success status
 */
export const deleteMessage = async (messageId, token) => {
  try {
    await api.delete(
      `/chat-history/${messageId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return {
      success: true
    };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to delete message'
    };
  }
};

export default { getChatHistory, getChatStats, deleteMessage };
