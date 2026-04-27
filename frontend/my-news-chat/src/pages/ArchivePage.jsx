import { useState, useEffect, useCallback } from "react";
import { getChatHistory, getChatStats, deleteMessage } from "../services/chatHistoryService";
import ArchiveHeader from "../components/ArchiveHeader";
import ArchiveControls from "../components/ArchiveControls";
import MessageGroup from "../components/MessageGroup";
import ExpandedMessageModal from "../components/ExpandedMessageModal";
import ArchiveEmptyState from "../components/ArchiveEmptyState";
import ArchiveLoadingState from "../components/ArchiveLoadingState";
import {
  buildConversationTurns,
  formatMessageDate,
  sortMessagesNewestFirst,
} from "../utils/dateTime";

export default function ArchivePage({ token, refreshMessages, removeMessage }) {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
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
      setError("Failed to load chat history");
      console.error("Error fetching chat history:", err);
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
      console.error("Error fetching stats:", err);
    }
  }, [token]);

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
      console.error("Error deleting message:", err);
      alert("Failed to delete message");
    }
  };

  const conversationTurns = buildConversationTurns(sortMessagesNewestFirst(chatHistory));

  const filteredConversationTurns = conversationTurns.filter((turn) => {
    const searchableText = `${turn.user?.text || ""} ${turn.assistant?.text || ""}`.toLowerCase();
    return searchableText.includes(searchTerm.toLowerCase());
  });

  const groupedByDate = filteredConversationTurns.reduce((acc, turn) => {
    const date = formatMessageDate(turn.created_at);
    if (!acc[date]) acc[date] = [];
    acc[date].push(turn);
    return acc;
  }, {});

  if (loading) {
    return <ArchiveLoadingState />;
  }

  return (
    <div className="app-shell min-h-screen px-4 py-4 sm:px-5 lg:px-6">
      <div className="mx-auto flex max-w-6xl flex-col gap-4">
        <ArchiveHeader stats={stats} />
        <ArchiveControls searchTerm={searchTerm} onSearchChange={setSearchTerm} />

        <div className="intel-card min-h-[40vh] p-4 sm:p-6">
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
    </div>
  );
}
