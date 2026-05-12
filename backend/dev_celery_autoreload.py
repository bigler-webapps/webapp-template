from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


WATCH_ROOT = Path("/app/backend")
POLL_SECONDS = 1.0
WATCH_SUFFIXES = {".py"}
IGNORED_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "media",
    "static",
    "staticfiles",
    "templates",
    "test_media",
}
CELERY_COMMAND = [
    "celery",
    "-A",
    "backend",
    "worker",
    "-l",
    "INFO",
    "--concurrency=1",
    "--max-tasks-per-child=1",
]

stop_requested = False


def signal_handler(signum, frame):
    global stop_requested
    stop_requested = True


def iter_watch_files(root: Path):
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if dirname not in IGNORED_DIRS
        )

        current_root_path = Path(current_root)
        for filename in sorted(filenames):
            path = current_root_path / filename
            if path.suffix not in WATCH_SUFFIXES:
                continue
            yield path


def snapshot_files(root: Path) -> dict[str, int]:
    snapshot: dict[str, int] = {}
    for path in iter_watch_files(root):
        try:
            snapshot[str(path)] = path.stat().st_mtime_ns
        except FileNotFoundError:
            continue
    return snapshot


def has_changes(previous: dict[str, int], current: dict[str, int]) -> bool:
    return previous != current


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> int:
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    print(f"[INFO] Starting celery auto-reload for {WATCH_ROOT}")
    snapshot_started_at = time.perf_counter()
    previous_snapshot = snapshot_files(WATCH_ROOT)
    snapshot_duration = time.perf_counter() - snapshot_started_at
    print(
        "[INFO] Celery auto-reload watching "
        f"{len(previous_snapshot)} Python files in {snapshot_duration:.2f}s"
    )

    while not stop_requested:
        print(f"[INFO] Starting celery worker: {' '.join(CELERY_COMMAND)}")
        process = subprocess.Popen(CELERY_COMMAND)

        while not stop_requested:
            if process.poll() is not None:
                if stop_requested:
                    break
                print(f"[WARN] Celery worker exited with code {process.returncode}, restarting...")
                time.sleep(1)
                previous_snapshot = snapshot_files(WATCH_ROOT)
                break

            time.sleep(POLL_SECONDS)
            current_snapshot = snapshot_files(WATCH_ROOT)
            if has_changes(previous_snapshot, current_snapshot):
                print("[INFO] Backend Python change detected. Restarting celery worker...")
                previous_snapshot = current_snapshot
                terminate_process(process)
                break

        if stop_requested:
            terminate_process(process)
            break

    print("[INFO] Celery auto-reload stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
