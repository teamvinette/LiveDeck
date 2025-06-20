#!/usr/bin/env bash
#
# start_mute_middleware.sh
#
# Starts the V1 mute middleware script once, in the background, without logs.
# Writes the PID to /tmp/mute_middleware.pid.
#
# Best practices:
#  - Prevent multiple instances via PID file check
#  - Use nohup to detach from terminal
#  - Redirect all output to /dev/null
#  - Exit immediately so the script doesn’t hang
#

### CONFIGURATION
SCRIPT_PATH="/path/to/your/livedeck/folder/LiveDeck.py"
PID_FILE="/tmp/mute_middleware.pid"
PYTHON_BIN="$(which python3)"

### ERROR CHECKS
# 1) Python script exists
if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "[ERROR] Script not found at $SCRIPT_PATH" >&2
  exit 1
fi

# 2) Python interpreter available
if [[ -z "$PYTHON_BIN" ]]; then
  echo "[ERROR] python3 not found in PATH" >&2
  exit 1
fi

### PREVENT MULTIPLE INSTANCES
if [[ -f "$PID_FILE" ]]; then
  old_pid=$(<"$PID_FILE")
  if ps -p "$old_pid" > /dev/null 2>&1; then
    echo "[WARN] Middleware already running (PID $old_pid)."
    exit 0
  else
    echo "[INFO] Removing stale PID file."
    rm -f "$PID_FILE"
  fi
fi

### START THE SERVICE
echo "[INFO] Launching mute middleware..."
# - nohup: ignore SIGHUP so it keeps running after you log out
# - redirect stdout and stderr to /dev/null
nohup "$PYTHON_BIN" "$SCRIPT_PATH" > /dev/null 2>&1 &

new_pid=$!
# Give the process a moment to start and verify it's still alive
sleep 0.1
if ! ps -p "$new_pid" > /dev/null 2>&1; then
  echo "[ERROR] Failed to start middleware (process died immediately)." >&2
  exit 1
fi

# Record its PID for later shutdown
echo "$new_pid" > "$PID_FILE"
echo "[INFO] Middleware started (PID $new_pid)."

exit 0
