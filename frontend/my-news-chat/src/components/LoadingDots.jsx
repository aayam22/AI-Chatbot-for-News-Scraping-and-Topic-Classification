import { useState, useEffect } from 'react';

export default function LoadingDots({ text = 'Generating' }) {
  const [dots, setDots] = useState('.');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === '.') return '..';
        if (prev === '..') return '...';
        if (prev === '...') return '....';
        return '.';
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <span style={{ display: 'inline-block' }}>
      ⏳ {text}{dots}
    </span>
  );
}
