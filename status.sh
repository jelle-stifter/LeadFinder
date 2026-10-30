#!/bin/bash
echo "--- Lead Finder Pro Service Status ---"
if ps aux | grep -v grep | grep -q "worker.py"; then
    echo "🟢 Worker: Running"
else
    echo "🔴 Worker: Stopped"
fi

if ps aux | grep -v grep | grep -q "streamlit run"; then
    echo "🟢 Dashboard: Running"
else
    echo "🔴 Dashboard: Stopped"
fi
