import ImageTooltip from './ImageTooltip';
import { STYLES } from '../constants/styles';

/**
 * SourceCard Component - Displays individual news source
 * Shows category, title, and optional image with hover tooltip
 */
export default function SourceCard({ source, onImageClick }) {
  if (!source) return null;

  return (
    <div style={STYLES.SOURCE_CONTAINER}>
      <div style={STYLES.SOURCE_TEXT}>
        <div style={STYLES.SOURCE_CATEGORY}>{source.category}</div>
        <div style={STYLES.SOURCE_TITLE}>{source.title}</div>
      </div>

      {source.image_url && (
        <ImageTooltip imageUrl={source.image_url} title={source.title}>
          <img
            src={source.image_url}
            alt={source.title}
            onClick={() => onImageClick(source.image_url)}
            style={STYLES.SOURCE_IMAGE}
          />
        </ImageTooltip>
      )}
    </div>
  );
}
