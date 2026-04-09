import { STYLES } from '../constants/styles';

/**
 * ImagePreview Component - Full-screen image preview modal
 * Closes on click or when previewImage is null
 */
export default function ImagePreview({ imageUrl, onClose }) {
  if (!imageUrl) return null;

  return (
    <div style={STYLES.PREVIEW_MODAL} onClick={onClose}>
      <img
        src={imageUrl}
        alt="preview"
        style={STYLES.PREVIEW_IMAGE}
      />
    </div>
  );
}
