const ArchiveControls = ({ searchTerm, onSearchChange }) => {
  return (
    <div className="intel-card p-4">
      <input
        type="text"
        placeholder="Search conversations..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        className="intel-input"
      />
    </div>
  );
};

export default ArchiveControls;
