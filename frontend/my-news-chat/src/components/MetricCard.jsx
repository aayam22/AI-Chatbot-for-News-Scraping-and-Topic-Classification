import { useState, memo } from 'react';
import PropTypes from 'prop-types';

/**
 * MetricCard - Displays a single metric with hover effect
 * Wrapped with memo to prevent unnecessary re-renders
 */
const MetricCard = memo(function MetricCard({ label, value, icon }) {
  const [isHovered, setIsHovered] = useState(false);

  const cardStyle = {
    padding: '16px',
    backgroundColor: '#fff',
    border: '3px solid #000',
    boxShadow: '3px 3px 0px rgba(0, 0, 0, 0.1)',
    transition: 'all 0.2s ease',
    cursor: 'default',
  };

  const cardHoverStyle = {
    ...cardStyle,
    boxShadow: '5px 5px 0px rgba(0, 0, 0, 0.15)',
    transform: 'translate(-2px, -2px)',
  };

  const labelStyle = {
    fontSize: '10px',
    fontWeight: '900',
    color: '#666',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginBottom: '8px',
    opacity: 0.7,
  };

  const valueStyle = {
    fontSize: '28px',
    fontWeight: '900',
    color: '#000',
    margin: '0 0 8px 0',
    lineHeight: '1.2',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  const iconStyle = {
    fontSize: '24px',
  };

  return (
    <div
      style={isHovered ? cardHoverStyle : cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={labelStyle}>{label}</div>
      <div style={valueStyle}>
        <span style={iconStyle}>{icon}</span>
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
