import { formatMessageTime } from "../utils/dateTime";

const ConversationItem = ({ turn, onExpand }) => {
  const previewText = (text) => {
    if (!text) {
      return "";
    }

    return text.length > 180 ? `${text.substring(0, 180)}...` : text;
  };

  const expandableMessage = turn.assistant ?? turn.user;

  return (
    <div
      className="mb-5 overflow-hidden rounded-[1.15rem] border-2 border-black bg-white shadow-[4px_4px_0_rgba(0,0,0,0.06)] transition hover:-translate-y-0.5"
      onClick={() => expandableMessage && onExpand(expandableMessage)}
    >
      {turn.user && (
        <div className="bg-zinc-950 px-5 py-4 text-white">
          <div className="mb-3 text-[11px] font-bold uppercase tracking-[0.12em] text-white/70">
            {formatMessageTime(turn.user.created_at)} - YOU
          </div>
          <div className="break-words text-sm leading-7">{previewText(turn.user.text)}</div>
        </div>
      )}

      {turn.assistant && (
        <div className="border-t-2 border-black bg-zinc-100 px-5 py-4 text-zinc-950">
          <div className="mb-3 text-[11px] font-bold uppercase tracking-[0.12em] text-zinc-500">
            {formatMessageTime(turn.assistant.created_at)} - ASSISTANT
          </div>
          <div className="break-words text-sm leading-7">{previewText(turn.assistant.text)}</div>
          {turn.assistant.sources && turn.assistant.sources.length > 0 && (
            <div className="mt-3 text-[11px] font-bold uppercase tracking-[0.12em] text-zinc-500">
              {turn.assistant.sources.length} source{turn.assistant.sources.length > 1 ? "s" : ""}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConversationItem;
