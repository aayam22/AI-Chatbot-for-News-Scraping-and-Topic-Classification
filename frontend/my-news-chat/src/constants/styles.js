// Reusable Style Objects
export const STYLES = {
  // Container Styles
  CHAT_CONTAINER: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    minHeight: '100vh',
    background:
      'radial-gradient(circle at top left, rgba(255,255,255,0.95), rgba(238,238,238,0.88) 34%, rgba(230,230,230,0.82) 100%)',
    fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif',
    color: '#111',
    padding: '20px',
    gap: '14px',
    overflow: 'hidden'
  },

  CHAT_HEADER: {
    maxWidth: '1240px',
    width: '100%',
    margin: '0 auto',
    border: '2px solid #111',
    background:
      'linear-gradient(135deg, rgba(255,255,255,0.92), rgba(244,244,244,0.9))',
    boxShadow: '10px 10px 0 rgba(0, 0, 0, 0.08)',
    padding: '22px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '18px',
    flexWrap: 'wrap'
  },

  CHAT_HEADER_KICKER: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '11px',
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: '0.16em',
    marginBottom: '12px',
    color: '#4b5563'
  },

  CHAT_HEADER_TITLE: {
    margin: 0,
    fontSize: 'clamp(1.9rem, 3vw, 3rem)',
    lineHeight: 0.95,
    fontWeight: '900',
    letterSpacing: '-0.06em',
    textTransform: 'uppercase'
  },

  CHAT_HEADER_SUBTITLE: {
    margin: '10px 0 0',
    maxWidth: '680px',
    fontSize: '14px',
    lineHeight: 1.6,
    color: '#4b5563',
    fontWeight: '500'
  },

  CHAT_STATUS_CARD: {
    minWidth: '220px',
    border: '2px solid #111',
    background: '#111',
    color: '#fff',
    padding: '14px 16px',
    display: 'grid',
    gap: '8px',
    alignSelf: 'stretch'
  },

  CHAT_STATUS_LABEL: {
    fontSize: '10px',
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: '0.16em',
    opacity: 0.72
  },

  CHAT_STATUS_VALUE: {
    fontSize: '15px',
    fontWeight: '700',
    lineHeight: 1.5
  },

  CHAT_PANEL: {
    flex: 1,
    maxWidth: '1240px',
    width: '100%',
    margin: '0 auto',
    border: '2px solid rgba(17, 17, 17, 0.92)',
    background: 'rgba(255,255,255,0.78)',
    boxShadow: '10px 10px 0 rgba(0, 0, 0, 0.08)',
    backdropFilter: 'blur(10px)',
    minHeight: 0,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden'
  },

  MESSAGES_AREA: {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column'
  },

  MESSAGES_INNER: {
    width: '100%',
    maxWidth: '1040px',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '18px'
  },

  INPUT_DOCK: {
    maxWidth: '1240px',
    width: '100%',
    margin: '0 auto',
    position: 'sticky',
    bottom: 0,
    zIndex: 5
  },

  INPUT_CONTAINER: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '10px',
    padding: '12px 14px',
    border: '2px solid #111',
    background: 'rgba(255,255,255,0.92)',
    boxShadow: '10px 10px 0 rgba(0, 0, 0, 0.08)',
    flexWrap: 'wrap'
  },

  INPUT_FIELD_WRAP: {
    flex: '1 1 460px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },

  INPUT_LABEL_ROW: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '12px',
    alignItems: 'center',
    flexWrap: 'wrap'
  },

  INPUT_LABEL: {
    fontSize: '10px',
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: '0.16em',
    color: '#4b5563'
  },

  INPUT_HINT: {
    fontSize: '11px',
    color: '#6b7280',
    fontWeight: '500'
  },

  // Message Styles
  MESSAGE_WRAPPER: (role) => ({
    display: 'flex',
    justifyContent: role === 'user' ? 'flex-end' : 'flex-start'
  }),

  MESSAGE_BOX: (role) => ({
    width: 'min(100%, 840px)',
    padding: '18px 20px',
    background:
      role === 'user'
        ? 'linear-gradient(135deg, #111, #242424)'
        : 'linear-gradient(135deg, rgba(255,255,255,0.98), rgba(246,246,246,0.92))',
    color: role === 'user' ? '#fff' : '#111',
    border: role === 'user' ? '2px solid #111' : '1px solid rgba(17, 17, 17, 0.12)',
    borderRadius: '22px',
    boxShadow:
      role === 'user'
        ? '0 18px 40px rgba(0, 0, 0, 0.16)'
        : '0 18px 40px rgba(15, 23, 42, 0.08)',
    wordWrap: 'break-word'
  }),

  MESSAGE_META: (role) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
    marginBottom: '12px',
    fontSize: '11px',
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: '0.14em',
    color: role === 'user' ? 'rgba(255,255,255,0.72)' : '#6b7280'
  }),

  MESSAGE_ROLE: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px'
  },

  MESSAGE_TEXT: {
    display: 'grid',
    gap: '12px',
    fontSize: '15px',
    lineHeight: 1.75,
    whiteSpace: 'normal'
  },

  MESSAGE_PARAGRAPH: {
    margin: 0
  },

  MESSAGE_BULLET: {
    display: 'grid',
    gridTemplateColumns: '14px 1fr',
    gap: '10px',
    alignItems: 'start'
  },

  MESSAGE_BULLET_DOT: {
    fontWeight: '900'
  },

  SOURCES_SECTION: {
    marginTop: '18px',
    paddingTop: '16px',
    borderTop: '1px solid rgba(107, 114, 128, 0.24)',
    display: 'grid',
    gap: '12px'
  },

  // Input Styles
  INPUT_FIELD: {
    flex: 1,
    width: '100%',
    minHeight: '44px',
    resize: 'none',
    padding: '10px 14px',
    border: '2px solid rgba(17, 17, 17, 0.18)',
    borderRadius: '14px',
    fontSize: '14px',
    lineHeight: 1.4,
    fontFamily: 'inherit',
    background: '#fff',
    color: '#111',
    outline: 'none'
  },

  BUTTON_GROUP: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap'
  },

  BUTTON: (variant = 'secondary') => ({
    minWidth: '110px',
    padding: '10px 14px',
    border: variant === 'primary' ? '2px solid #111' : '2px solid rgba(17, 17, 17, 0.12)',
    borderRadius: '14px',
    background: variant === 'primary' ? '#111' : '#f4f4f4',
    color: variant === 'primary' ? '#fff' : '#111',
    cursor: 'pointer',
    fontWeight: '800',
    fontFamily: 'inherit',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    fontSize: '12px',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease',
    boxShadow:
      variant === 'primary'
        ? '0 14px 30px rgba(17, 17, 17, 0.18)'
        : '0 10px 24px rgba(15, 23, 42, 0.06)'
  }),

  // Source Styles
  SOURCE_CONTAINER: {
    display: 'flex',
    alignItems: 'stretch',
    justifyContent: 'space-between',
    gap: '14px',
    padding: '14px',
    background: 'rgba(243, 244, 246, 0.95)',
    border: '1px solid rgba(17, 17, 17, 0.08)',
    borderRadius: '18px'
  },

  SOURCE_TEXT: {
    flex: 1,
    display: 'grid',
    gap: '8px',
    alignContent: 'start'
  },

  SOURCE_CATEGORY: {
    display: 'inline-flex',
    width: 'fit-content',
    padding: '5px 10px',
    borderRadius: '999px',
    background: '#111',
    color: '#fff',
    fontSize: '10px',
    fontWeight: '800',
    letterSpacing: '0.12em',
    textTransform: 'uppercase'
  },

  SOURCE_TITLE: {
    fontWeight: '700',
    fontSize: '15px',
    lineHeight: 1.45
  },

  SOURCE_IMAGE: {
    width: '88px',
    minWidth: '88px',
    height: '88px',
    objectFit: 'cover',
    borderRadius: '14px',
    cursor: 'pointer',
    border: '1px solid rgba(17, 17, 17, 0.08)'
  },

  SOURCES_HEADER: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
    fontSize: '12px',
    color: '#6b7280',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.12em'
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
    padding: '28px',
    background:
      'linear-gradient(135deg, rgba(255,255,255,0.98), rgba(245,245,245,0.9))',
    border: '2px dashed rgba(17, 17, 17, 0.24)',
    borderRadius: '22px',
    textAlign: 'left',
    color: '#4b5563',
    display: 'grid',
    gap: '12px'
  },

  EMPTY_STATE_TITLE: {
    margin: 0,
    color: '#111',
    fontSize: '20px',
    fontWeight: '900',
    letterSpacing: '-0.04em',
    textTransform: 'uppercase'
  },

  EMPTY_STATE_TEXT: {
    margin: 0,
    fontSize: '14px',
    lineHeight: 1.7
  },

  EMPTY_STATE_TIPS: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    marginTop: '4px'
  },

  EMPTY_STATE_TIP: {
    padding: '8px 12px',
    background: '#111',
    color: '#fff',
    borderRadius: '999px',
    fontSize: '12px',
    fontWeight: '700'
  }
};
