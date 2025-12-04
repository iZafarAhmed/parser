#!/usr/bin/env bash

echo "Installing Playwright Chromium..."
python -m playwright install --with-deps chromium

echo "Starting FastAPI server..."
exec uvicorn app:app --host 0.0.0.0 --port $PORT
