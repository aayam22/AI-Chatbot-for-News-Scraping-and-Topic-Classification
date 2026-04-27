import { formatMessageDateTime } from "../utils/dateTime";

const ExpandedMessageModal = ({ message, onClose, onDelete }) => {
  if (!message) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onClick={onClose}>
      <div
        className="relative max-h-[80vh] w-full max-w-2xl overflow-y-auto border-4 border-black bg-white p-6 shadow-[10px_10px_0_#000]"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center border-2 border-black bg-white text-base font-black transition hover:-translate-y-0.5"
          onClick={onClose}
        >
          X
        </button>
        <div className="mt-6">
          <div className="text-[11px] font-bold uppercase tracking-[0.12em] text-zinc-500">
            {formatMessageDateTime(message.created_at)} - {message.role === "user" ? "YOUR QUESTION" : "RESPONSE"}
          </div>
          <div className="mt-4 whitespace-pre-wrap text-sm leading-8 text-zinc-800">
            {message.text}
          </div>
          {message.sources && message.sources.length > 0 && (
            <div className="mt-5">
              <div className="intel-kicker mb-3">Sources</div>
              {message.sources.map((source, idx) => (
                <div
                  key={idx}
                  className="mb-2 rounded-2xl bg-zinc-100 px-4 py-3 text-sm font-medium text-zinc-700"
                >
                  {source.title || source.category}
                </div>
              ))}
            </div>
          )}
          <button
            type="button"
            className="mt-5 w-full rounded-2xl border border-red-300 bg-red-500 px-4 py-3 text-xs font-extrabold uppercase tracking-[0.14em] text-white transition hover:-translate-y-0.5 hover:bg-red-600"
            onClick={() => onDelete(message.id)}
          >
            DELETE MESSAGE
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExpandedMessageModal;
