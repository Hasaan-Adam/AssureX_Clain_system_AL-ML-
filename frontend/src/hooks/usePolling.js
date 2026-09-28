import { useEffect, useRef } from 'react';

/**
 * Hook to poll an async function at regular intervals with pause condition
 */
export const usePolling = (callback, intervalMs = 10000, enabled = true) => {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled || intervalMs === null) return;

    const tick = () => {
      if (savedCallback.current) {
        savedCallback.current();
      }
    };

    const id = setInterval(tick, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, enabled]);
};

export default usePolling;