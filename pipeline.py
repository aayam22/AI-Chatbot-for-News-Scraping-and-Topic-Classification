"""
Master news pipeline.

Automates:
1. Scraping
2. Classification
3. Embedding + FAISS
"""

import argparse
import importlib
import io
import re
import sys
import time
from contextlib import redirect_stderr, redirect_stdout


DEFAULT_MODE = "full"
VALID_MODES = {"full", "fast"}
PROGRESS_INTERVAL = 10
PROGRESS_TIME_SECONDS = 3.0

TQDM_PROGRESS_RE = re.compile(
    r"^(?P<label>[^:]+):\s+\d+%\|.*?\|\s+(?P<current>\d+)/(?P<total>\d+)"
)


def clean_log_line(line):
    cleaned = line.replace("\t", " ").strip()
    cleaned = re.sub(r"^[^A-Za-z0-9\[]+\s*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class PipelineLogRouter(io.TextIOBase):
    def __init__(self, stream):
        self.stream = stream
        self.buffer = ""
        self.progress_state = {}
        self.reported_hf_retry = False

    def write(self, text):
        if not text:
            return 0

        self.buffer += text
        parts = re.split(r"(\r|\n)", self.buffer)
        self.buffer = ""

        pending = ""
        for index in range(0, len(parts), 2):
            chunk = parts[index]
            separator = parts[index + 1] if index + 1 < len(parts) else ""

            if separator:
                self._handle_line(pending + chunk)
                pending = ""
            else:
                pending += chunk

        self.buffer = pending
        return len(text)

    def flush(self):
        if self.buffer.strip():
            self._handle_line(self.buffer)
        self.buffer = ""
        self.stream.flush()

    def _handle_line(self, raw_line):
        if not raw_line:
            return

        if "ProtocolError(" in raw_line or "ConnectionResetError(" in raw_line:
            if not self.reported_hf_retry:
                self._emit("Model download/cache check retried after a network interruption.")
                self.reported_hf_retry = True
            return

        if "Retrying in " in raw_line and "huggingface.co" in raw_line:
            if not self.reported_hf_retry:
                self._emit("Model download/cache check retried after a network interruption.")
                self.reported_hf_retry = True
            return

        if "requesting HEAD https://huggingface.co" in raw_line:
            if not self.reported_hf_retry:
                self._emit("Model download/cache check retried after a network interruption.")
                self.reported_hf_retry = True
            return

        progress_match = TQDM_PROGRESS_RE.match(raw_line.strip())
        if progress_match:
            label = clean_log_line(progress_match.group("label"))
            current = int(progress_match.group("current"))
            total = int(progress_match.group("total"))
            now = time.time()

            state = self.progress_state.get(
                label,
                {"current": 0, "last_emitted": 0, "last_emit_time": 0.0},
            )
            state["current"] = current

            should_emit = (
                current == total
                or current - state["last_emitted"] >= PROGRESS_INTERVAL
                or now - state["last_emit_time"] >= PROGRESS_TIME_SECONDS
            )

            if should_emit:
                self._emit(f"{label}: {current}/{total}")
                state["last_emitted"] = current
                state["last_emit_time"] = now

            self.progress_state[label] = state
            return

        cleaned = clean_log_line(raw_line)
        if not cleaned:
            return

        if cleaned == "Device set to use cuda:0":
            cleaned = "Using GPU: cuda:0"

        self._emit(cleaned)

    def _emit(self, line):
        print(line, file=self.stream, flush=True)


def run_module(module_name, step_name):
    print(f"\nRunning {step_name}...", flush=True)
    start = time.time()

    router = PipelineLogRouter(sys.stdout)

    try:
        with redirect_stdout(router), redirect_stderr(router):
            module = importlib.import_module(module_name)

            if hasattr(module, "main"):
                module.main()
            else:
                raise AttributeError(f"{module_name}.py has no main() function")

    except Exception as exc:
        print(f"{step_name} failed: {exc}", flush=True)
        raise
    finally:
        router.flush()

    end = time.time()
    print(f"{step_name} completed in {round(end - start, 2)} seconds", flush=True)


def run_scraper():
    run_module("scrapper", "Scraping")


def run_classifier():
    run_module("classifier", "Classification")


def run_embedder():
    run_module("embedder", "Embedding + FAISS")


def run_pipeline(mode=DEFAULT_MODE):
    total_start = time.time()

    print("\n==============================", flush=True)
    print("STARTING NEWS AI PIPELINE", flush=True)
    print(f"Mode: {mode.upper()}", flush=True)
    print("==============================\n", flush=True)

    try:
        if mode == "full":
            run_scraper()
            run_classifier()
            run_embedder()
        elif mode == "fast":
            run_classifier()
            run_embedder()
        else:
            raise ValueError("Invalid mode. Use 'full' or 'fast'.")

    except Exception as exc:
        print("\nPIPELINE FAILED", flush=True)
        print(f"Error: {exc}", flush=True)
        return 1

    total_end = time.time()

    print("\n==============================", flush=True)
    print("PIPELINE COMPLETED SUCCESSFULLY", flush=True)
    print(f"Total time: {round(total_end - total_start, 2)} seconds", flush=True)
    print("==============================\n", flush=True)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="Run the news data pipeline.")
    parser.add_argument(
        "--mode",
        default=DEFAULT_MODE,
        choices=sorted(VALID_MODES),
        help="Pipeline mode: 'full' runs scraping, classification, and embedding; 'fast' skips scraping.",
    )
    return parser.parse_args()


def main(mode=DEFAULT_MODE):
    return run_pipeline(mode)


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.mode))
