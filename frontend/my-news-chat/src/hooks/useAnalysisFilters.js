import { useState, useCallback } from 'react';

/**
 * Custom hook for managing analysis filter state
 * @returns {Object} Filter state and setters
 */
export function useAnalysisFilters() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedSource, setSelectedSource] = useState(null);
  const [dateFrom, setDateFrom] = useState(null);
  const [dateTo, setDateTo] = useState(null);

  const resetFilters = useCallback(() => {
    setSelectedCategory(null);
    setSelectedSource(null);
    setDateFrom(null);
    setDateTo(null);
  }, []);

  const getFilterParams = useCallback(() => {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (selectedCategory) params.append('category', selectedCategory);
    if (selectedSource) params.append('source', selectedSource);
    return params;
  }, [dateFrom, dateTo, selectedCategory, selectedSource]);

  return {
    selectedCategory,
    setSelectedCategory,
    selectedSource,
    setSelectedSource,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    resetFilters,
    getFilterParams,
  };
}
