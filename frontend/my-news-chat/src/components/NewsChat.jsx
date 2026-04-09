import { useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ImagePreview from './ImagePreview';
import useChat from '../hooks/useChat';
import { STYLES } from '../constants/styles';
import { STORAGE_KEYS } from '../constants/config';

/**
 * NewsChat Component - Main chat interface
 * Orchestrates message display, input, and images
 * Uses custom hooks for clean, modular logic
 */
export default function NewsChat({ messages, setMessages }) {
  const [previewImage, setPreviewImage] = useState(null);
  const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
  const { sendQuestion, clearChat } = useChat(setMessages, token);

  const handleClearChat = async () => {
    await clearChat();
    localStorage.removeItem(STORAGE_KEYS.CHAT_MESSAGES);
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