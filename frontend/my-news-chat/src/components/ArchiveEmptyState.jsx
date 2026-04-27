const ArchiveEmptyState = ({ error, searchTerm }) => {
  if (error) {
    return (
      <div className="flex min-h-[24rem] items-center justify-center rounded-[1.5rem] border border-red-200 bg-red-50 px-6 text-center text-base font-bold text-red-700">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-[24rem] items-center justify-center rounded-[1.5rem] border border-dashed border-black/20 bg-white/70 px-6 text-center text-base font-bold text-zinc-500">
      <p>{searchTerm ? "No matching conversations" : "No chat history yet"}</p>
    </div>
  );
};

export default ArchiveEmptyState;
