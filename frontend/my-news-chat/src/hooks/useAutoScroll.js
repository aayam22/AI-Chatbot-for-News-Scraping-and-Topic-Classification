import { useEffect, useRef } from 'react';

/**
 * Custom hook for auto-scrolling to latest message
 */
export const useAutoScroll = (dependency) => {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [dependency]);

  return endRef;
};

export default useAutoScroll;
