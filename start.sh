#!/bin/bash
echo "Starting Lead Finder Pro..."
pkill -f worker.py 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true

cd /home/jelle/leadfinder
nohup python3 worker.py > worker.log 2>&1 &
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &

echo "Services started successfully."
echo "Dashboard: http://100.76.239.38:8501"

