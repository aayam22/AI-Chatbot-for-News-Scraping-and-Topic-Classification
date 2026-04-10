/**
 * AnalysisCard Component - Card for displaying individual analytics metrics
 * Shows a single metric with title, value, and optional subtitle
 */
import React, { useState } from 'react';

export default function AnalysisCard({ title, value, subtitle, icon }) {
  const cardStyle = {
    padding: '24px',
    backgroundColor: '#fff',
    border: '3px solid #000',
    borderRadius: '4px',
    boxShadow: '4px 4px 0px rgba(0, 0, 0, 0.1)',
    fontFamily: '"Space Grotesk", sans-serif',
    flex: '1',
    minWidth: '250px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    transition: 'all 0.2s ease',
    cursor: 'default'
  };

  const cardHoverStyle = {
    ...cardStyle,
    boxShadow: '6px 6px 0px rgba(0, 0, 0, 0.15)',
    transform: 'translate(-2px, -2px)'
  };

  const titleStyle = {
    fontSize: '12px',
    fontWeight: '900',
    textTransform: 'uppercase',
    opacity: 0.6,
    marginBottom: '8px',
    letterSpacing: '1px'
  };

  const valueStyle = {
    fontSize: '36px',
    fontWeight: '900',
    margin: '8px 0',
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  };

  const iconStyle = {
    fontSize: '40px',
    lineHeight: '1'
  };

  const subtitleStyle = {
    fontSize: '13px',
    opacity: 0.7,
    marginTop: '8px',
    fontWeight: '500'
  };

  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      style={isHovered ? cardHoverStyle : cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={titleStyle}>{title}</div>
      <div style={valueStyle}>
        {icon && <span style={iconStyle}>{icon}</span>}
        <span>{value}</span>
      </div>
      {subtitle && <div style={subtitleStyle}>{subtitle}</div>}
    </div>
  );
}
