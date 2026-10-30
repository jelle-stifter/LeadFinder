# 🎯 B2B Lead Finder Pro

An autonomous, local B2B lead discovery and enrichment web application hosted on Raspberry Pi. Built using Python, Streamlit, OpenStreetMap (Overpass API), DuckDuckGo Search, and SQLite.

## ✨ Features
* **Zero API Costs:** Discovers local businesses without dedicated websites via OpenStreetMap and DuckDuckGo without relying on paid APIs or credit cards.
* **Manual Enrichment Workflow:** Direct Google Maps shortcuts per lead to quickly record ratings, review counts, and customized opportunity scores.
* **Online Presence & Status Management:** Track web presence (e.g., website/profile availability) and mark closed businesses (temporary/permanent).
* **Archiving System:** Dedicated archive management tab with custom filtering and simple restoration options.
* **Streamlit Dashboard:** Interactive tabular editor with real-time KPI metrics and live background worker logs.

## 🚀 Quickstart

### Prerequisites
```bash
pip install streamlit pandas requests duckduckgo_search

