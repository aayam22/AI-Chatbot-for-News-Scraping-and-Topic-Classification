import NewsChat from '../components/NewsChat';

/**
 * ChatPage Component - Main chat application page
 * Wraps NewsChat component with page-level layout
 */
export default function ChatPage({ messages, setMessages, token, refreshMessages }) {
  return (
    <NewsChat
      messages={messages}
      setMessages={setMessages}
      token={token}
      refreshMessages={refreshMessages}
    />
  );
}
