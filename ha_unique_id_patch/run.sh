#!/bin/sh

echo "[INFO] Starting HA Unique ID Patch Addon..."
echo "[INFO] Current directory: $(pwd)"
echo "[INFO] File list:"
ls -F /app

# Loop to restart python app if it crashes, but sleep to avoid restart loop limit
while true; do
  echo "[INFO] Installing/Checking requirements..."
  pip install --no-cache-dir --break-system-packages requests
  pip install --no-cache-dir --break-system-packages -r /app/requirements.txt
  
  echo "[INFO] Launching Python application..."
  python3 -u /app/main.py
  EXIT_CODE=$?
  echo "[ERROR] Python application crashed with exit code $EXIT_CODE"
  echo "[INFO] Sleeping for 60 seconds before restart..."
  sleep 60
done
