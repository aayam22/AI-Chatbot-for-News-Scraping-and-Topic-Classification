import { useState } from 'react';

export default function ImageTooltip({ children, imageUrl, title }) {
  const [isHovering, setIsHovering] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseEnter = (e) => {
    setIsHovering(true);
    updateMousePos(e);
  };

  const handleMouseMove = (e) => {
    updateMousePos(e);
  };

  const updateMousePos = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({
      x: rect.right + 10,
      y: rect.top - 20
    });
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <div
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setIsHovering(false)}
      >
        {children}
      </div>

      {/* TOOLTIP POPUP */}
      {isHovering && (
        <div
          style={{
            position: 'fixed',
            left: `${mousePos.x}px`,
            top: `${mousePos.y}px`,
            background: '#fff',
            border: '1px solid #ddd',
            borderRadius: '6px',
            padding: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: 1000,
            pointerEvents: 'none'
          }}
        >
          <img
            src={imageUrl}
            alt={title}
            style={{
              maxWidth: '150px',
              maxHeight: '120px',
              borderRadius: '4px',
              display: 'block'
            }}
          />
          {title && (
            <div
              style={{
                fontSize: '11px',
                marginTop: '6px',
                color: '#666',
                maxWidth: '150px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {title}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
