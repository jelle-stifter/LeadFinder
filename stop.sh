#!/bin/bash
echo "Stopping Lead Finder Pro services..."
pkill -f worker.py 2>/dev/null || true
pkill -f "streamlit run" 2>/dev/null || true
echo "Services stopped successfully."
