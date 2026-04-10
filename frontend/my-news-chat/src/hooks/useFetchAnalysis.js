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

  const fetchAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_CONFIG.BACKEND_URL}/analyze?${filterParams.toString()}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch analysis data');
      }

      const data = await response.json();
      console.log('Analysis data received:', data);
      setAnalysisData(data);
    } catch (err) {
      console.error('Analysis fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filterParams]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    analysisData,
    loading,
    error,
    refetch: fetchAnalysis,
  };
}
