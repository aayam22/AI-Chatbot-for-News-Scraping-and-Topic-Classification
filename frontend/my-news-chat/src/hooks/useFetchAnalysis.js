import { useState, useEffect, useCallback } from 'react';
import { API_CONFIG } from '../constants/config';

/**
 * Custom hook for fetching analysis data
 * @param {URLSearchParams} filterParams - Filter parameters for API request
 * @returns {Object} { analysisData, loading, error, refetch }
 */
export function useFetchAnalysis(filterParams) {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalysis = useCallback(async (signal) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/analyze?${filterParams.toString()}`,
        { signal }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch analysis data');
      }

      const data = await response.json();

      if (signal?.aborted) {
        return;
      }

      setAnalysisData(data);
    } catch (err) {
      if (err.name === 'AbortError') {
        return;
      }

      console.error('Analysis fetch error:', err);
      setAnalysisData(null);
      setError(err.message);
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  }, [filterParams]);

  useEffect(() => {
    const controller = new AbortController();

    fetchAnalysis(controller.signal);

    return () => {
      controller.abort();
    };
  }, [fetchAnalysis]);

  return {
    analysisData,
    loading,
    error,
    refetch: () => fetchAnalysis(),
  };
}
