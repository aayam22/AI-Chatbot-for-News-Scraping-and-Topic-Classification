import NewsChat from '../components/NewsChat';

/**
 * ChatPage Component - Main chat application page
 * Wraps NewsChat component with page-level layout
 */
export default function ChatPage({
  messages,
  setMessages,
  clearVisibleMessages,
  token,
  refreshMessages
}) {
  return (
    <NewsChat
      messages={messages}
      setMessages={setMessages}
      clearVisibleMessages={clearVisibleMessages}
      token={token}
      refreshMessages={refreshMessages}
    />
  );
}
