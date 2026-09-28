import { useState, useEffect, useCallback } from 'react';

/**
 * Generic async fetch hook with auto-execution and manual refetch
 */
export const useFetch = (fetchFn, deps = [], autoFetch = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn(...args);
      const payload = result && result.data !== undefined ? result.data : result;
      setData(payload);
      return payload;
    } catch (err) {
      const errMsg = err.message || 'Error loading data';
      setError(errMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    if (autoFetch) {
      execute();
    }
  }, [execute, autoFetch]);

  return { data, loading, error, refetch: execute, setData };
};

export default useFetch;