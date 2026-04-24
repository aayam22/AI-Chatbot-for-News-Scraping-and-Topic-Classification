import { useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ImagePreview from './ImagePreview';
import useChat from '../hooks/useChat';
import { STYLES } from '../constants/styles';

/**
 * NewsChat Component - Main chat interface
 * Orchestrates message display, input, and images
 * Uses custom hooks for clean, modular logic
 */
export default function NewsChat({ messages, setMessages, token, refreshMessages }) {
  const [previewImage, setPreviewImage] = useState(null);
  const { sendQuestion, clearChat } = useChat(setMessages, token, refreshMessages);

  const handleClearChat = async () => {
    await clearChat();
  };

  return (
    <div style={STYLES.CHAT_CONTAINER}>
      <MessageList
        messages={messages}
        onImageClick={(imageUrl) => setPreviewImage(imageUrl)}
      />

      <ChatInput
        onSend={sendQuestion}
        onClear={handleClearChat}
        disabled={!token}
      />

      <ImagePreview
        imageUrl={previewImage}
        onClose={() => setPreviewImage(null)}
      />
    </div>
  );
}
