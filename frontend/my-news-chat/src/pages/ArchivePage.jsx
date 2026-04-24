import { useState, useEffect, useCallback } from 'react';
import { getChatHistory, getChatStats, deleteMessage } from '../services/chatHistoryService';
import ArchiveHeader from '../components/ArchiveHeader';
import ArchiveControls from '../components/ArchiveControls';
import MessageGroup from '../components/MessageGroup';
import ExpandedMessageModal from '../components/ExpandedMessageModal';
import ArchiveEmptyState from '../components/ArchiveEmptyState';
import ArchiveLoadingState from '../components/ArchiveLoadingState';
import { buildConversationTurns, formatMessageDate, sortMessagesNewestFirst } from '../utils/dateTime';

export default function ArchivePage({ token, refreshMessages, removeMessage }) {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedMessage, setExpandedMessage] = useState(null);

  const fetchChatHistory = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getChatHistory(token, 1000, 0);

      if (!result.success) {
        throw new Error(result.error);
      }

      setChatHistory(sortMessagesNewestFirst(result.data.messages || []));
      setError(null);
    } catch (err) {
      setError('Failed to load chat history');
      console.error('Error fetching chat history:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchChatStats = useCallback(async () => {
    try {
      const result = await getChatStats(token);

      if (!result.success) {
        throw new Error(result.error);
      }

      setStats(result.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  }, [token]);

  // Fetch chat history
  useEffect(() => {
    fetchChatHistory();
    fetchChatStats();
  }, [fetchChatHistory, fetchChatStats]);

  const handleDeleteMessage = async (messageId) => {
    try {
      const result = await deleteMessage(messageId, token);

      if (!result.success) {
        throw new Error(result.error);
      }

      setChatHistory((prev) => prev.filter((msg) => msg.id !== messageId));
      removeMessage?.(messageId);
      setExpandedMessage(null);
      fetchChatStats();

      if (refreshMessages) {
        await refreshMessages();
      }
    } catch (err) {
      console.error('Error deleting message:', err);
      alert('Failed to delete message');
    }
  };

  const conversationTurns = buildConversationTurns(sortMessagesNewestFirst(chatHistory));

  // Filter conversations while keeping each question/answer pair intact
  const filteredConversationTurns = conversationTurns.filter((turn) => {
    const searchableText = `${turn.user?.text || ''} ${turn.assistant?.text || ''}`.toLowerCase();
    return searchableText.includes(searchTerm.toLowerCase());
  });

  // Group conversations by date
  const groupedByDate = filteredConversationTurns.reduce((acc, turn) => {
    const date = formatMessageDate(turn.created_at);
    if (!acc[date]) acc[date] = [];
    acc[date].push(turn);
    return acc;
  }, {});

  const archiveContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#fff',
    fontFamily: '"Space Grotesk", sans-serif',
  };

  const messagesContainerStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    backgroundColor: '#fff',
  };

  if (loading) {
    return <ArchiveLoadingState />;
  }

  return (
    <div style={archiveContainerStyle}>
      <ArchiveHeader stats={stats} />
      <ArchiveControls 
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
      />
      <div style={messagesContainerStyle}>
        {error && <ArchiveEmptyState error={error} searchTerm={searchTerm} />}
        {filteredConversationTurns.length === 0 && !error && (
          <ArchiveEmptyState error={null} searchTerm={searchTerm} />
        )}
        {Object.entries(groupedByDate).map(([date, conversations]) => (
          <MessageGroup 
            key={date} 
            date={date} 
            conversations={conversations}
            onExpandMessage={setExpandedMessage}
          />
        ))}
      </div>
      <ExpandedMessageModal 
        message={expandedMessage}
        onClose={() => setExpandedMessage(null)}
        onDelete={handleDeleteMessage}
      />
    </div>
  );
}
