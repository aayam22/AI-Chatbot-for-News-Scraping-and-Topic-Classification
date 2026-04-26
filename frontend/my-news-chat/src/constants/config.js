// API Configuration
export const API_CONFIG = {
  BACKEND_URL: 'http://127.0.0.1:8000',
  ENDPOINTS: {
    ASK: '/ask',
    CLEAR_MEMORY: '/clear-memory',
    PIPELINE_STATUS: '/system/pipeline-status',
    PIPELINE_RUN: '/system/pipeline/run'
  },
  TIMEOUT: 30000
};

// UI Configuration
export const UI_CONFIG = {
  MESSAGE_MAX_WIDTH: '75%',
  SOURCES_LIMIT: 3,
  IMAGE_TOOLTIP_WIDTH: 150,
  IMAGE_TOOLTIP_HEIGHT: 120,
  LOADING_DOT_INTERVAL: 500
};

// Token storage key
export const STORAGE_KEYS = {
  TOKEN: 'token',
  CHAT_MESSAGES: 'chat_messages',
  CHAT_PAGE_CLEARED_AT: 'chat_page_cleared_at'
};
