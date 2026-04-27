import ImageTooltip from './ImageTooltip';

/**
 * SourceCard Component - Displays individual news source
 * Shows category, title, and optional image with hover tooltip
 */
export default function SourceCard({ source, onImageClick }) {
  if (!source) return null;

  return (
    <div className="flex flex-col gap-4 rounded-[1.15rem] border border-black/8 bg-zinc-100/90 p-4 sm:flex-row sm:items-stretch sm:justify-between">
      <div className="grid flex-1 gap-2">
        <div className="intel-chip w-fit">{source.category}</div>
        <div className="text-sm font-bold leading-6 text-zinc-900">{source.title}</div>
      </div>

      {source.image_url && (
        <ImageTooltip imageUrl={source.image_url} title={source.title}>
          <img
            src={source.image_url}
            alt={source.title}
            onClick={() => onImageClick(source.image_url)}
            className="h-[88px] w-full cursor-pointer rounded-2xl border border-black/8 object-cover sm:w-[88px]"
          />
        </ImageTooltip>
      )}
    </div>
  );
}
