/**
 * ImagePreview Component - Full-screen image preview modal
 * Closes on click or when previewImage is null
 */
export default function ImagePreview({ imageUrl, onClose }) {
  if (!imageUrl) return null;

  return (
    <div
      className="fixed inset-0 z-[999] flex items-center justify-center bg-black/75 p-4"
      onClick={onClose}
    >
      <img
        src={imageUrl}
        alt="preview"
        className="max-h-[90vh] max-w-[90vw] rounded-2xl shadow-2xl"
      />
    </div>
  );
}
