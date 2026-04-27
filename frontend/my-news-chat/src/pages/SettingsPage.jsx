import { useEffect, useRef, useState } from "react";
import { getPipelineStatus, runPipeline } from "../services/pipelineService";

const LABELS = {
  idle: "Idle",
  running: "Running",
  succeeded: "Completed",
  failed: "Failed",
};

const STATUS_COLORS = {
  idle: "#39424e",
  running: "#8a5a00",
  succeeded: "#0f6a3e",
  failed: "#9a1f19",
};

const MODE_OPTIONS = [
  {
    value: "full",
    label: "Full pipeline",
    description: "Run scraping, classification, and embeddings.",
  },
  {
    value: "fast",
    label: "Fast refresh",
    description: "Skip scraping and reuse the current stored articles.",
  },
];

function formatTimestamp(value) {
  if (!value) {
    return "Not available";
  }

  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? value : timestamp.toLocaleString();
}

export default function SettingsPage({ token }) {
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [selectedMode, setSelectedMode] = useState("full");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const outputRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    const loadStatus = async (silent = false) => {
      if (!silent) {
        setIsLoading(true);
      }

      const result = await getPipelineStatus(token);
      if (!isMounted) {
        return;
      }

      if (result.success) {
        setPipelineStatus(result.data);
        setError("");
      } else {
        setError(result.error);
      }

      if (!silent) {
        setIsLoading(false);
      }
    };

    loadStatus();
    const intervalId = window.setInterval(() => loadStatus(true), 1000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, [token]);

  useEffect(() => {
    if (!outputRef.current) {
      return;
    }

    outputRef.current.scrollTop = outputRef.current.scrollHeight;
  }, [pipelineStatus?.output]);

  const handleRunPipeline = async () => {
    setIsSubmitting(true);
    setError("");
    setNotice("");

    const result = await runPipeline(token, selectedMode);

    if (result.success) {
      setPipelineStatus(result.data);
      setNotice(
        `Pipeline started in ${selectedMode} mode. Live updates will appear below.`
      );
    } else {
      setError(result.error);
    }

    setIsSubmitting(false);
  };

  const currentStatus = pipelineStatus?.status ?? "idle";
  const isRunning = currentStatus === "running";
  const statusText = LABELS[currentStatus] ?? "Unknown";
  const statusColor = STATUS_COLORS[currentStatus] ?? "#39424e";
  const outputText =
    pipelineStatus?.output?.trim() ||
    "No pipeline logs yet. Start a run to capture output here.";

  return (
    <main className="app-shell min-h-screen p-4 sm:p-5 lg:p-6">
      <div className="mx-auto grid max-w-6xl gap-5">
        <section className="intel-card p-5 lg:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="intel-kicker mb-3">Settings</p>
              <h1 className="intel-panel-title">Manual Data Pipeline Trigger</h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-zinc-600">
                Run the backend news pipeline on demand from the frontend. The
                full mode includes scraping, while fast mode only refreshes
                classification and embeddings from existing data.
              </p>
            </div>

            <div className="min-w-[180px] border-2 border-black bg-zinc-950 p-4 text-white">
              <div className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-white/70">
                Current Status
              </div>
              <div className="mt-4 inline-flex items-center gap-3 text-lg font-black" style={{ color: statusColor }}>
                <span
                  style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "999px",
                    backgroundColor: statusColor,
                    display: "inline-block",
                  }}
                />
                {statusText}
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-2">
          <div className="intel-card p-5">
            <h2 className="mb-5 text-2xl font-black tracking-[-0.05em] text-zinc-950">
              Pipeline Controls
            </h2>

            <div className="grid gap-3">
              {MODE_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className={`rounded-[1.2rem] border-2 px-4 py-4 transition ${
                    selectedMode === option.value
                      ? "border-black bg-zinc-950 text-white"
                      : "border-black bg-white text-zinc-900"
                  } ${isRunning ? "cursor-not-allowed opacity-65" : "cursor-pointer"}`}
                >
                  <input
                    type="radio"
                    name="pipeline-mode"
                    value={option.value}
                    checked={selectedMode === option.value}
                    onChange={(event) => setSelectedMode(event.target.value)}
                    disabled={isRunning}
                    className="mr-3"
                  />
                  <strong>{option.label}</strong>
                  <div className="mt-2 text-sm leading-6">{option.description}</div>
                </label>
              ))}
            </div>

            <button
              type="button"
              onClick={handleRunPipeline}
              disabled={isRunning || isSubmitting || isLoading}
              className={`mt-5 w-full rounded-2xl border-2 border-black px-4 py-4 text-sm font-black uppercase tracking-[0.12em] transition ${
                isRunning
                  ? "cursor-not-allowed bg-[#bfb8af] text-zinc-500"
                  : "bg-zinc-950 text-white shadow-[6px_6px_0_#111] hover:-translate-y-0.5"
              }`}
            >
              {isSubmitting
                ? "Starting pipeline..."
                : isRunning
                  ? "Pipeline already running"
                  : "Run pipeline now"}
            </button>

            {notice ? <p className="mt-4 text-sm font-bold text-emerald-700">{notice}</p> : null}
            {error ? <p className="mt-4 text-sm font-bold text-red-700">{error}</p> : null}
          </div>

          <div className="intel-card p-5">
            <h2 className="mb-5 text-2xl font-black tracking-[-0.05em] text-zinc-950">
              Run Details
            </h2>

            {isLoading && !pipelineStatus ? (
              <p className="m-0 text-sm text-zinc-600">Loading pipeline status...</p>
            ) : (
              <div className="grid gap-3 text-sm leading-7 text-zinc-700">
                <div>
                  <strong>Selected mode:</strong> {pipelineStatus?.mode ?? selectedMode}
                </div>
                <div>
                  <strong>Last started:</strong> {formatTimestamp(pipelineStatus?.started_at)}
                </div>
                <div>
                  <strong>Last finished:</strong> {formatTimestamp(pipelineStatus?.finished_at)}
                </div>
                <div>
                  <strong>Triggered by:</strong> {pipelineStatus?.last_triggered_by ?? "Not available"}
                </div>
                <div>
                  <strong>Exit code:</strong> {pipelineStatus?.exit_code ?? "Not available"}
                </div>
                <div>
                  <strong>Last update:</strong> {formatTimestamp(pipelineStatus?.updated_at)}
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="intel-card p-5">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="mb-1 text-2xl font-black tracking-[-0.05em] text-zinc-950">
                Pipeline Output
              </h2>
              <p className="text-sm leading-6 text-zinc-600">
                Logs stream here while the pipeline is running. Keep this page
                open to follow progress in near real time.
              </p>
            </div>
            <div className="rounded-full border-2 border-black bg-white px-4 py-2 text-xs font-bold uppercase tracking-[0.14em] text-zinc-700">
              Refresh: every 1 second
            </div>
          </div>

          <pre
            ref={outputRef}
            className="m-0 min-h-[280px] max-h-[420px] overflow-auto border-2 border-black bg-zinc-950 p-5 text-[13px] leading-7 whitespace-pre-wrap break-words text-[#f7f1e7]"
          >
            {outputText}
          </pre>
        </section>
      </div>
    </main>
  );
}
