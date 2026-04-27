import { memo } from "react";
import PropTypes from "prop-types";

const MetricCard = memo(function MetricCard({ label, value, icon }) {
  return (
    <div className="intel-card p-4 transition duration-200 hover:-translate-y-0.5 hover:shadow-[12px_12px_0_rgba(0,0,0,0.1)]">
      <div className="intel-kicker mb-3">{label}</div>
      <div className="flex items-center gap-3 text-[1.9rem] font-black leading-none text-zinc-950">
        <span className="inline-flex rounded-full border border-black/10 bg-zinc-100 px-3 py-2 text-sm font-extrabold tracking-[0.14em] text-zinc-600">
          {icon}
        </span>
        <span>{value}</span>
      </div>
    </div>
  );
});

MetricCard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  icon: PropTypes.string.isRequired,
};

export default MetricCard;
