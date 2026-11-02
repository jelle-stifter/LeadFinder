#!/bin/bash
cd /home/jelle/leadfinder
python3 worker.py > worker.log 2>&1 &
python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
wait -n
