import { formatMessageDateShort } from "../utils/dateTime";

const ArchiveHeader = ({ stats }) => {
  return (
    <div className="intel-card p-5 lg:p-6">
      <p className="intel-kicker mb-3">Conversation history</p>
      <h1 className="intel-panel-title text-[clamp(2rem,4vw,2.8rem)]">ARCHIVE</h1>
      <p className="mt-3 max-w-3xl text-sm font-medium leading-7 text-zinc-600">
        Review saved conversations, reopen context quickly, and inspect source-backed replies from past sessions.
      </p>
      {stats && (
        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-[1.25rem] border border-black/10 bg-white/75 p-4">
            <span className="intel-kicker">Total Messages</span>
            <span className="mt-2 block text-2xl font-black text-zinc-950">{stats.total_messages}</span>
          </div>
          <div className="rounded-[1.25rem] border border-black/10 bg-white/75 p-4">
            <span className="intel-kicker">Your Questions</span>
            <span className="mt-2 block text-2xl font-black text-zinc-950">{stats.user_messages}</span>
          </div>
          <div className="rounded-[1.25rem] border border-black/10 bg-white/75 p-4">
            <span className="intel-kicker">Responses</span>
            <span className="mt-2 block text-2xl font-black text-zinc-950">{stats.assistant_messages}</span>
          </div>
          {stats.first_message && (
            <div className="rounded-[1.25rem] border border-black/10 bg-white/75 p-4">
              <span className="intel-kicker">Since</span>
              <span className="mt-2 block text-2xl font-black text-zinc-950">
                {formatMessageDateShort(stats.first_message)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ArchiveHeader;
