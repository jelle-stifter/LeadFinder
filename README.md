# 🎯 B2B Lead Finder Pro

An autonomous, self-hosted B2B lead discovery and enrichment web application designed for Raspberry Pi. Built using Python, Streamlit, OpenStreetMap (Overpass API), DuckDuckGo Search, and SQLite.

This tool automatically scans local regions for businesses operating without dedicated websites, provides direct Google Maps integration for manual review/enrichment, and offers a clean Streamlit UI for outreach tracking and status archiving—all with zero paid API fees.

## ✨ Key Features
Zero API Costs: Discovers local businesses via OpenStreetMap (Overpass API) and verifies web presence via DuckDuckGo without requiring credit cards or Google Cloud API keys.

Manual Enrichment Workflow: Direct Google Maps shortcuts per lead to quickly record ratings, review counts, and customized opportunity scores.

Online Presence & Status Tracking: Track web presence (e.g., website/social profile availability) and flag closed businesses (temporary or permanent).

Built-in Archiving System: Archive closed or non-viable leads with full status filtering and one-click restoration options.

Streamlit Management Dashboard: Interactive data editor with real-time KPI metrics and live background worker activity logs.

Lightweight Background Daemon: Background process running on Raspberry Pi, accessible locally or remotely via Tailscale.

## 🛠️ Prerequisites & Installation
1. System Requirements
Raspberry Pi (or any Linux/Debian host) with Python 3.9+ installed.

Optional: Tailscale for secure remote access without port forwarding.

2. Install Required Python Packages
Run the following command in your terminal:

pip install streamlit pandas requests duckduckgo_search

## 📖 Complete Step-by-Step Usage Guide
### Step 1: Initial Launch
Start the background worker and the Streamlit web dashboard using the provided management script:

./start.sh

Access the dashboard in your web browser at http://<YOUR_PI_IP>:8501 (e.g., http://100.76.239.38:8501 via Tailscale).

### Step 2: Configure Search Parameters
Open the dashboard and navigate to the ⚙️ Niches & Cities tab in the sidebar.

Add Target Cities: Enter the names of the cities/regions you want to search (e.g., Maasmechelen, Genk, Hasselt).

Add Target Niches: Enter OpenStreetMap craft/shop/office/amenity tags (e.g., carpenter, electrician, plumber, painter, tiler).

Remove Unwanted Targets: Select any city or niche under the current list dropdowns and click 🗑️ Remove to delete them from cities.json or niches.json.

### Step 3: Autonomous Scanning Process
The background worker continuously scans the specified cities and niches via Overpass API.

It verifies whether discovered businesses have a dedicated website using DuckDuckGo search automation.

Businesses without a website are saved directly to leads.db.

You can monitor real-time worker logs in the Live Activity widget in the sidebar.

### Step 4: Review and Enrich Leads
Navigate to the 📊 Leads Database tab in the dashboard.

Click the 📍 Maps link for any lead. This opens the exact company search directly in Google Maps in a new browser tab.

Inspect the business listing for Google rating, total review count, and overall business viability.

Return to the dashboard table and directly enter:

Rating (e.g., 4.8 ⭐)

Reviews count

Score (0-100): Your personal evaluation of the conversion potential.

### Step 5: Managing Outreach & Online Presence
Calling Workflow: After attempting outreach, check the Called? box and update the Call Status dropdown.

Online Presence / Status Tracking: Update the Online Presence / Status dropdown according to your findings (e.g., Neither Website nor Profile, Has Website, No Social Profile, Has Profile, No Website, Both Present, Temporarily Closed, Permanently Closed).

### Step 6: Archiving Closed or Non-Viable Businesses
To remove a closed, duplicate, or irrelevant lead from the active view, check the ❌ Archive? box in the first column.

Click 💾 Save Changes below the table. The selected leads will immediately move to the archive.

Go to the 🗑️ Closed / Archived tab to review archived leads.

Filter archived entries by status/presence or uncheck Archived? to restore a lead back to the primary dashboard.

### Step 7: Save & Export
Persist Data: Always click 💾 Save Changes after making edits in either tab.

Export Data: Click the 📥 Export Selection to CSV button to download filtered lead lists for cold outreach campaigns.

## 🛠️ Service Management Scripts
The repository includes executable control scripts for background operation:

## Start All Services:
./start.sh

## Check Service Status:
./status.sh

## Stop All Services:
./stop.sh

## 📁 Repository Structure
leadfinder/

├── app.py           # Streamlit frontend dashboard & data editor

├── worker.py        # Background scanning worker (OSM & DuckDuckGo)

├── start.sh         # Application & service startup script

├── stop.sh          # Service shutdown script

├── status.sh        # Service health check script

├── README.md        # Documentation and workflow guide

├── .gitignore       # Excludes local databases and log files from Git

├── cities.json      # Target cities configuration

└── niches.json      # Target business niches configuration
