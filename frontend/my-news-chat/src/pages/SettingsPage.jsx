import { useEffect, useRef, useState } from "react";
import { getPipelineStatus, runPipeline } from "../services/pipelineService";

const PAGE_STYLE = {
  minHeight: "100vh",
  background:
    "linear-gradient(135deg, #f7f1e7 0%, #e6ddd0 45%, #d6cab8 100%)",
  color: "#151515",
  padding: "32px",
  fontFamily: '"Space Grotesk", sans-serif',
};

const PANEL_STYLE = {
  backgroundColor: "rgba(255, 255, 255, 0.84)",
  border: "3px solid #111",
  boxShadow: "8px 8px 0 #111",
  padding: "24px",
};

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
    <main style={PAGE_STYLE}>
      <div
        style={{
          maxWidth: "1080px",
          margin: "0 auto",
          display: "grid",
          gap: "24px",
        }}
      >
        <section style={PANEL_STYLE}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <p
                style={{
                  margin: "0 0 8px",
                  fontSize: "12px",
                  fontWeight: "700",
                  letterSpacing: "0.18em",
                  textTransform: "uppercase",
                }}
              >
                Settings
              </p>
              <h1
                style={{
                  margin: "0 0 12px",
                  fontSize: "clamp(2rem, 4vw, 3rem)",
                  lineHeight: 1,
                }}
              >
                Manual Data Pipeline Trigger
              </h1>
              <p
                style={{
                  margin: 0,
                  maxWidth: "700px",
                  fontSize: "16px",
                  lineHeight: 1.6,
                }}
              >
                Run the backend news pipeline on demand from the frontend. The
                full mode includes scraping, while fast mode only refreshes
                classification and embeddings from existing data.
              </p>
            </div>

            <div
              style={{
                minWidth: "180px",
                padding: "14px 16px",
                border: "2px solid #111",
                backgroundColor: "#fff",
              }}
            >
              <div
                style={{
                  fontSize: "12px",
                  fontWeight: "700",
                  letterSpacing: "0.14em",
                  textTransform: "uppercase",
                  marginBottom: "10px",
                }}
              >
                Current Status
              </div>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "10px",
                  color: statusColor,
                  fontWeight: "900",
                  fontSize: "18px",
                }}
              >
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

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "24px",
          }}
        >
          <div style={PANEL_STYLE}>
            <h2 style={{ marginTop: 0, marginBottom: "18px", fontSize: "24px" }}>
              Pipeline Controls
            </h2>

            <div style={{ display: "grid", gap: "14px" }}>
              {MODE_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  style={{
                    border: "2px solid #111",
                    padding: "14px 16px",
                    backgroundColor:
                      selectedMode === option.value ? "#111" : "#f7f1e7",
                    color: selectedMode === option.value ? "#fff" : "#111",
                    cursor: isRunning ? "not-allowed" : "pointer",
                    opacity: isRunning ? 0.65 : 1,
                  }}
                >
                  <input
                    type="radio"
                    name="pipeline-mode"
                    value={option.value}
                    checked={selectedMode === option.value}
                    onChange={(event) => setSelectedMode(event.target.value)}
                    disabled={isRunning}
                    style={{ marginRight: "10px" }}
                  />
                  <strong>{option.label}</strong>
                  <div style={{ marginTop: "6px", fontSize: "14px", lineHeight: 1.5 }}>
                    {option.description}
                  </div>
                </label>
              ))}
            </div>

            <button
              type="button"
              onClick={handleRunPipeline}
              disabled={isRunning || isSubmitting || isLoading}
              style={{
                marginTop: "20px",
                width: "100%",
                padding: "16px",
                border: "2px solid #111",
                backgroundColor: isRunning ? "#bfb8af" : "#111",
                color: isRunning ? "#555" : "#fff",
                fontWeight: "900",
                fontSize: "15px",
                cursor: isRunning ? "not-allowed" : "pointer",
                boxShadow: isRunning ? "none" : "6px 6px 0 #111",
              }}
            >
              {isSubmitting
                ? "Starting pipeline..."
                : isRunning
                  ? "Pipeline already running"
                  : "Run pipeline now"}
            </button>

            {notice ? (
              <p style={{ marginTop: "16px", color: "#0f6a3e", fontWeight: "700" }}>
                {notice}
              </p>
            ) : null}

            {error ? (
              <p style={{ marginTop: "16px", color: "#9a1f19", fontWeight: "700" }}>
                {error}
              </p>
            ) : null}
          </div>

          <div style={PANEL_STYLE}>
            <h2 style={{ marginTop: 0, marginBottom: "18px", fontSize: "24px" }}>
              Run Details
            </h2>

            {isLoading && !pipelineStatus ? (
              <p style={{ margin: 0 }}>Loading pipeline status...</p>
            ) : (
              <div style={{ display: "grid", gap: "14px" }}>
                <div>
                  <strong>Selected mode:</strong> {pipelineStatus?.mode ?? selectedMode}
                </div>
                <div>
                  <strong>Last started:</strong>{" "}
                  {formatTimestamp(pipelineStatus?.started_at)}
                </div>
                <div>
                  <strong>Last finished:</strong>{" "}
                  {formatTimestamp(pipelineStatus?.finished_at)}
                </div>
                <div>
                  <strong>Triggered by:</strong>{" "}
                  {pipelineStatus?.last_triggered_by ?? "Not available"}
                </div>
                <div>
                  <strong>Exit code:</strong>{" "}
                  {pipelineStatus?.exit_code ?? "Not available"}
                </div>
                <div>
                  <strong>Last update:</strong>{" "}
                  {formatTimestamp(pipelineStatus?.updated_at)}
                </div>
              </div>
            )}
          </div>
        </section>

        <section style={PANEL_STYLE}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
              flexWrap: "wrap",
              marginBottom: "16px",
            }}
          >
            <div>
              <h2 style={{ margin: "0 0 6px", fontSize: "24px" }}>Pipeline Output</h2>
              <p style={{ margin: 0, color: "#444", lineHeight: 1.5 }}>
                Logs stream here while the pipeline is running. Keep this page
                open to follow progress in near real time.
              </p>
            </div>
            <div
              style={{
                padding: "8px 12px",
                border: "2px solid #111",
                backgroundColor: "#fff",
                fontWeight: "700",
              }}
            >
              Refresh: every 1 second
            </div>
          </div>

          <pre
            ref={outputRef}
            style={{
              margin: 0,
              padding: "18px",
              minHeight: "280px",
              maxHeight: "420px",
              overflow: "auto",
              backgroundColor: "#111",
              color: "#f7f1e7",
              border: "2px solid #111",
              fontSize: "13px",
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {outputText}
          </pre>
        </section>
      </div>
    </main>
  );
}
