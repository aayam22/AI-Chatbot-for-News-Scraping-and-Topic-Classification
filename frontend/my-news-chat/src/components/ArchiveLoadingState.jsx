const ArchiveLoadingState = () => {
  return (
    <div className="app-shell min-h-screen px-4 py-4 sm:px-5 lg:px-6">
      <div className="intel-card mx-auto max-w-6xl p-6">
        <h1 className="intel-panel-title text-[clamp(2rem,4vw,2.8rem)]">ARCHIVE</h1>
        <p className="mt-3 text-sm font-medium text-zinc-600">Loading chat history...</p>
      </div>
    </div>
  );
};

export default ArchiveLoadingState;
