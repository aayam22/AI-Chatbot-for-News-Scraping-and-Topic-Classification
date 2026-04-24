import { useState, useEffect, useCallback } from 'react';
import { getChatHistory, getChatStats, deleteMessage } from '../services/chatHistoryService';
import ArchiveHeader from '../components/ArchiveHeader';
import ArchiveControls from '../components/ArchiveControls';
import MessageGroup from '../components/MessageGroup';
import ExpandedMessageModal from '../components/ExpandedMessageModal';
import ArchiveEmptyState from '../components/ArchiveEmptyState';
import ArchiveLoadingState from '../components/ArchiveLoadingState';

export default function ArchivePage({ token, refreshMessages, removeMessage }) {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [expandedMessage, setExpandedMessage] = useState(null);

  const fetchChatHistory = useCallback(async () => {
    try {
      setLoading(true);
      const result = await getChatHistory(token, 1000, 0);

      if (!result.success) {
        throw new Error(result.error);
      }

      setChatHistory(result.data.messages || []);
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

  // Filter messages
  const filteredMessages = chatHistory.filter(msg => {
    const matchesSearch = msg.text.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = activeFilter === 'all' || msg.role === activeFilter;
    return matchesSearch && matchesFilter;
  });

  // Group messages by date
  const groupedByDate = filteredMessages.reduce((acc, msg) => {
    const date = new Date(msg.created_at).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    if (!acc[date]) acc[date] = [];
    acc[date].push(msg);
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
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
      />
      <div style={messagesContainerStyle}>
        {error && <ArchiveEmptyState error={error} searchTerm={searchTerm} />}
        {filteredMessages.length === 0 && !error && (
          <ArchiveEmptyState error={null} searchTerm={searchTerm} />
        )}
        {Object.entries(groupedByDate).map(([date, messages]) => (
          <MessageGroup 
            key={date} 
            date={date} 
            messages={messages}
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
