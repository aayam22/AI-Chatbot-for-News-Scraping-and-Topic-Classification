import { useState } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ImagePreview from './ImagePreview';
import useChat from '../hooks/useChat';

/**
 * NewsChat Component - Main chat interface
 * Orchestrates message display, input, and images
 * Uses custom hooks for clean, modular logic
 */
export default function NewsChat({
  messages,
  setMessages,
  clearVisibleMessages,
  token,
  refreshMessages
}) {
  const [previewImage, setPreviewImage] = useState(null);
  const { sendQuestion, clearChat } = useChat(
    setMessages,
    clearVisibleMessages,
    token,
    refreshMessages
  );

  const handleClearChat = async () => {
    await clearChat();
  };

  return (
    <div className="flex min-h-screen flex-col gap-4 px-4 py-4 sm:px-5 lg:px-6">
      <header className="intel-card mx-auto grid w-full max-w-6xl gap-5 p-5 lg:grid-cols-[minmax(0,1fr)_240px] lg:p-6">
        <div>
          <div className="intel-kicker mb-3">Live briefing interface</div>
          <h1 className="intel-panel-title">INTEL FEED</h1>
          <p className="mt-3 max-w-3xl text-sm font-medium leading-7 text-zinc-600">
            Ask for breaking headlines, topic-specific summaries, and source-backed answers from the current news corpus.
          </p>
        </div>

        <div className="flex flex-col justify-between border-2 border-black bg-zinc-950 p-4 text-white">
          <div className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-white/70">
            Session status
          </div>
          <div className="space-y-2">
            <p className="text-sm font-bold leading-6">
              {token ? "Authenticated and ready for live queries." : "Sign in required to continue."}
            </p>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-white/70">
              {messages.length} message{messages.length === 1 ? "" : "s"} in view
            </p>
          </div>
        </div>
      </header>

      <div className="intel-card mx-auto flex w-full max-w-6xl min-h-0 flex-1 flex-col overflow-hidden">
        <MessageList
          messages={messages}
          onImageClick={(imageUrl) => setPreviewImage(imageUrl)}
        />
      </div>

      <div className="sticky bottom-0 z-10 mx-auto w-full max-w-6xl pb-1">
        <ChatInput
          onSend={sendQuestion}
          onClear={handleClearChat}
          disabled={!token}
        />
      </div>

      <ImagePreview
        imageUrl={previewImage}
        onClose={() => setPreviewImage(null)}
      />
    </div>
  );
}
