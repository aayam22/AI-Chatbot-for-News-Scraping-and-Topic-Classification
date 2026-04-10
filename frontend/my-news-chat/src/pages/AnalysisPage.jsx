import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useMemo } from 'react';
import { useAnalysisFilters } from '../hooks/useAnalysisFilters';
import { useFetchAnalysis } from '../hooks/useFetchAnalysis';
import FilterPanel from '../components/FilterPanel';
import MetricsSection from '../components/MetricsSection';
import ChartsSection from '../components/ChartsSection';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

/**
 * AnalysisPage - Analytics Dashboard matching INTEL_CORE chat theme
 * Refactored to use custom hooks and extracted components
 */
export default function AnalysisPage() {
  // Use custom hook for filter state management
  const {
    selectedCategory,
    setSelectedCategory,
    selectedSource,
    setSelectedSource,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    getFilterParams,
  } = useAnalysisFilters();

  // Build filter params (triggers refetch when filters change)
  const filterParams = useMemo(() => getFilterParams(), [getFilterParams]);

  // Use custom hook for data fetching
  const { analysisData, loading, error } = useFetchAnalysis(filterParams);


  // Memoize chart options to prevent unnecessary recalculations
  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        labels: {
          font: { family: '"Space Grotesk", sans-serif', weight: '600', size: 11 },
          padding: 12,
          usePointStyle: true,
          color: '#000',
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { font: { family: '"Space Grotesk", sans-serif', weight: '600', size: 11 }, color: '#000' },
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
      },
      x: {
        ticks: { font: { family: '"Space Grotesk", sans-serif', weight: '600', size: 11 }, color: '#000' },
        grid: { color: 'rgba(0, 0, 0, 0.1)' },
      },
    },
  }), []);

  // Prepare derived data with safe defaults
  const categoryDist = analysisData?.category_distribution || {};
  const sourceDist = analysisData?.source_distribution || {};
  const availableCategories = analysisData?.available_categories || [];
  const availableSources = analysisData?.available_sources || [];

  // Inline styles
  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: '#f8f8f8',
    fontFamily: '"Space Grotesk", sans-serif',
  };

  const contentStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  };

  const headerStyle = {
    borderBottom: '3px solid #000',
    paddingBottom: '16px',
  };

  const titleStyle = {
    fontSize: '24px',
    fontWeight: '900',
    margin: 0,
    marginBottom: '4px',
    letterSpacing: '-1px',
  };

  const subtitleStyle = {
    fontSize: '12px',
    fontWeight: '600',
    opacity: 0.6,
    margin: 0,
    textTransform: 'uppercase',
    letterSpacing: '1px',
  };

  const loadingStyle = {
    padding: '40px',
    textAlign: 'center',
    color: '#000',
    fontSize: '16px',
    fontWeight: '600',
    backgroundColor: '#fff',
    border: '2px solid #000',
  };

  const errorStyle = {
    padding: '16px',
    backgroundColor: '#fff',
    border: '3px solid #000',
    color: '#c00',
    fontWeight: '600',
    fontSize: '14px',
  };

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={contentStyle}>
          <div style={loadingStyle}>⏳ Loading analytics...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <div style={contentStyle}>
          <div style={errorStyle}>❌ Error: {error}</div>
        </div>
      </div>
    );
  }

  // No data state
  if (!analysisData) {
    return (
      <div style={containerStyle}>
        <div style={contentStyle}>
          <div style={errorStyle}>❌ No data available</div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={contentStyle}>
        {/* Header */}
        <div style={headerStyle}>
          <h1 style={titleStyle}>◒ ANALYTICS</h1>
          <p style={subtitleStyle}>Real-time article data & trends</p>
        </div>

        {/* Filters */}
        <FilterPanel
          dateFrom={dateFrom}
          onDateFromChange={setDateFrom}
          dateTo={dateTo}
          onDateToChange={setDateTo}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          availableCategories={availableCategories}
          selectedSource={selectedSource}
          onSourceChange={setSelectedSource}
          availableSources={availableSources}
        />

        {/* Key Metrics */}
        <MetricsSection
          analysisData={analysisData}
          categoryDist={categoryDist}
          sourceDist={sourceDist}
        />

        {/* Charts */}
        <ChartsSection analysisData={analysisData} chartOptions={chartOptions} />
      </div>
    </div>
  );
}

