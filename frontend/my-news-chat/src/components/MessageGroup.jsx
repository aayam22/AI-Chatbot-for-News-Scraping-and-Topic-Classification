import ConversationItem from "./ConversationItem";

const MessageGroup = ({ date, conversations, onExpandMessage }) => {
  return (
    <div className="mb-8">
      <div className="mb-4 border-b-2 border-black pb-2 text-sm font-black uppercase tracking-[0.12em] text-zinc-950">
        {date}
      </div>
      {conversations.map((conversation) => (
        <ConversationItem
          key={conversation.id}
          turn={conversation}
          onExpand={onExpandMessage}
        />
      ))}
    </div>
  );
};

export default MessageGroup;
