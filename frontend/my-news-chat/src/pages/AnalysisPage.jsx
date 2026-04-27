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
} from "chart.js";
import { useMemo } from "react";
import { useAnalysisFilters } from "../hooks/useAnalysisFilters";
import { useFetchAnalysis } from "../hooks/useFetchAnalysis";
import FilterPanel from "../components/FilterPanel";
import MetricsSection from "../components/MetricsSection";
import ChartsSection from "../components/ChartsSection";

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

export default function AnalysisPage() {
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

  const filterParams = useMemo(() => getFilterParams(), [getFilterParams]);
  const { analysisData, loading, error } = useFetchAnalysis(filterParams);

  const chartOptions = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          labels: {
            font: { family: '"Space Grotesk", sans-serif', weight: "600", size: 11 },
            padding: 12,
            usePointStyle: true,
            color: "#000",
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            font: { family: '"Space Grotesk", sans-serif', weight: "600", size: 11 },
            color: "#000",
          },
          grid: { color: "rgba(0, 0, 0, 0.1)" },
        },
        x: {
          ticks: {
            font: { family: '"Space Grotesk", sans-serif', weight: "600", size: 11 },
            color: "#000",
          },
          grid: { color: "rgba(0, 0, 0, 0.1)" },
        },
      },
    }),
    []
  );

  const categoryDist = analysisData?.category_distribution || {};
  const sourceDist = analysisData?.source_distribution || {};
  const availableCategories = analysisData?.available_categories || [];
  const availableSources = analysisData?.available_sources || [];

  if (loading) {
    return (
      <div className="app-shell min-h-screen p-4 sm:p-5 lg:p-6">
        <div className="intel-card mx-auto max-w-6xl p-10 text-center text-base font-semibold">
          Loading analytics...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-shell min-h-screen p-4 sm:p-5 lg:p-6">
        <div className="intel-card mx-auto max-w-6xl border-red-400 p-6 text-sm font-semibold text-red-700">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="app-shell min-h-screen p-4 sm:p-5 lg:p-6">
        <div className="intel-card mx-auto max-w-6xl p-6 text-sm font-semibold text-zinc-700">
          No data available
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell min-h-screen p-4 sm:p-5 lg:p-6">
      <div className="mx-auto flex max-w-6xl flex-col gap-5">
        <div className="intel-card grid gap-5 p-5 lg:grid-cols-[minmax(0,1fr)_220px] lg:p-6">
          <div>
            <p className="intel-kicker mb-3">Real-time article intelligence</p>
            <h1 className="intel-panel-title">ANALYTICS</h1>
            <p className="mt-3 max-w-3xl text-sm font-medium leading-7 text-zinc-600">
              Track source coverage, article volume, topic distribution, and date range trends in the same INTEL_CORE visual system.
            </p>
          </div>

          <div className="border-2 border-black bg-zinc-950 p-4 text-white">
            <div className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-white/70">
              Snapshot
            </div>
            <div className="mt-4 text-3xl font-black">
              {(analysisData?.total_articles || 0).toLocaleString()}
            </div>
            <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-white/70">
              indexed articles
            </p>
          </div>
        </div>

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

        <MetricsSection
          analysisData={analysisData}
          categoryDist={categoryDist}
          sourceDist={sourceDist}
        />

        <ChartsSection analysisData={analysisData} chartOptions={chartOptions} />
      </div>
    </div>
  );
}
