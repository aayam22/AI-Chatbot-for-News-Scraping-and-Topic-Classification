// Reusable Style Objects
export const STYLES = {
  // Container Styles
  CHAT_CONTAINER: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: '#f8f8f8'
  },

  MESSAGES_AREA: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px'
  },

  INPUT_CONTAINER: {
    display: 'flex',
    padding: '12px',
    borderTop: '1px solid #ddd',
    background: '#fff',
    gap: '8px'
  },

  // Message Styles
  MESSAGE_WRAPPER: (role) => ({
    display: 'flex',
    justifyContent: role === 'user' ? 'flex-end' : 'flex-start'
  }),

  MESSAGE_BOX: (role) => ({
    padding: '12px 16px',
    background: role === 'user' ? '#000' : '#fff',
    color: role === 'user' ? '#fff' : '#000',
    border: '1px solid #ddd',
    borderRadius: '8px',
    maxWidth: '75%',
    wordWrap: 'break-word'
  }),

  // Input Styles
  INPUT_FIELD: {
    flex: 1,
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '14px',
    fontFamily: 'inherit'
  },

  BUTTON: {
    padding: '10px 16px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    background: '#fff',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'all 0.2s'
  },

  // Source Styles
  SOURCE_CONTAINER: {
    display: 'flex',
    gap: '10px',
    marginTop: '8px'
  },

  SOURCE_TEXT: {
    flex: 1
  },

  SOURCE_CATEGORY: {
    fontSize: '11px',
    color: '#999'
  },

  SOURCE_TITLE: {
    fontWeight: '600',
    marginTop: '2px'
  },

  SOURCE_IMAGE: {
    width: '60px',
    height: '60px',
    objectFit: 'cover',
    borderRadius: '4px',
    cursor: 'pointer'
  },

  SOURCES_HEADER: {
    fontSize: '12px',
    color: '#999',
    marginTop: '8px'
  },

  // Modal/Preview Styles
  PREVIEW_MODAL: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'rgba(0,0,0,0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999
  },

  PREVIEW_IMAGE: {
    maxWidth: '90%',
    maxHeight: '90%',
    borderRadius: '8px'
  },

  // Empty State
  EMPTY_STATE: {
    padding: '20px',
    background: '#fff',
    border: '1px solid #ddd',
    borderRadius: '8px',
    textAlign: 'center',
    color: '#666'
  }
};
