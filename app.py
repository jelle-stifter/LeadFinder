import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import json
import os
import urllib.parse

st.set_page_config(page_title="Lead Finder Pro", layout="wide", page_icon="🎯")

st.markdown("""
    <style>
    .stMetric {
        background-color: #1e222a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3440;
    }
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

DB_PATH = "/home/jelle/leadfinder/leads.db"
CITIES_PATH = "/home/jelle/leadfinder/cities.json"
NICHES_PATH = "/home/jelle/leadfinder/niches.json"
LOG_PATH = "/home/jelle/leadfinder/worker.log"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def is_worker_running():
    try:
        output = subprocess.check_output(["ps", "aux"]).decode()
        return "worker.py" in output
    except Exception:
        return False

def get_last_logs(n_lines=5):
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-n_lines:])
        except Exception:
            return "Error reading log file."
    return "No log file found."

st.sidebar.title("🎯 Lead Finder Pro")

if is_worker_running():
    st.sidebar.success("🟢 **Worker:** Active")
else:
    st.sidebar.error("🔴 **Worker:** Stopped")

page_selection = st.sidebar.radio(
    "Navigation",
    ["📊 Leads Database", "🗑️ Closed / Archived", "⚙️ Niches & Cities"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Live Activity")
st.sidebar.code(get_last_logs(5), language="text")

if st.sidebar.button("🔄 Refresh"):
    st.rerun()

cities = load_json(CITIES_PATH, ["Maasmechelen"])
niches = load_json(NICHES_PATH, ["carpenter"])

if page_selection == "📊 Leads Database":
    st.title("🎯 B2B Lead Intelligence Dashboard")
    st.caption("Review leads on Google Maps and manually record ratings, review counts, and opportunity scores.")

    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM leads WHERE is_deleted = 0 OR is_deleted IS NULL ORDER BY eigen_score DESC, id DESC", conn)
    conn.close()

    if df.empty:
        st.info("No active leads found in the database.")
    else:
        defaults = {
            "gebeld": 0, "call_result": "-", "notes": "",
            "maps_url": "", "sterren": 0.0, "aantal_reviews": 0, "eigen_score": 50, "is_deleted": 0, "online_presence": "-"
        }
        for col, val in defaults.items():
            if col not in df.columns:
                df[col] = val

        df["gebeld"] = df["gebeld"].astype(bool)
        df["is_deleted"] = df["is_deleted"].astype(bool)

        df["maps_url"] = df.apply(
            lambda r: r["maps_url"] if r["maps_url"] else f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(r['naam']) + ' ' + str(r['stad']))}", 
            axis=1
        )

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_leads = len(df)
        to_call = len(df[df["gebeld"] == False])
        hot_leads = len(df[df["eigen_score"] >= 70])
        deals = len(df[df["call_result"].str.contains("Deal", na=False)])

        kpi1.metric("Total Leads", total_leads)
        kpi2.metric("Pending Calls", to_call)
        kpi3.metric("🔥 Hot Leads (70+)", hot_leads)
        kpi4.metric("✔️ Deals Closed", deals)

        st.markdown("---")

        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            all_cities = ["All Cities"] + sorted(list(set(df["stad"].dropna().tolist())))
            selected_city = st.selectbox("📍 Filter by City:", all_cities)

        with f_col2:
            all_niches = ["All Niches"] + sorted(list(set(df["niche"].dropna().tolist())))
            selected_niche = st.selectbox("🛠️ Filter by Niche:", all_niches)

        with f_col3:
            status_filter = st.selectbox(
                "📞 Call Status Filter:",
                ["All", "Pending Calls Only", "✔️ Deals", "❌ No Interest", "➖ No Answer"]
            )

        filtered_df = df.copy()
        if selected_city != "All Cities":
            filtered_df = filtered_df[filtered_df["stad"] == selected_city]
        if selected_niche != "All Niches":
            filtered_df = filtered_df[filtered_df["niche"] == selected_niche]

        if status_filter == "Pending Calls Only":
            filtered_df = filtered_df[filtered_df["gebeld"] == False]
        elif status_filter == "✔️ Deals":
            filtered_df = filtered_df[filtered_df["call_result"].str.contains("Deal", na=False)]
        elif status_filter == "❌ No Interest":
            filtered_df = filtered_df[filtered_df["call_result"].str.contains("No interest", na=False)]
        elif status_filter == "➖ No Answer":
            filtered_df = filtered_df[filtered_df["call_result"].str.contains("No answer", na=False)]

        st.write(f"Displayed leads: **{len(filtered_df)}**")

        edited_df = st.data_editor(
            filtered_df,
            column_order=[
                "is_deleted", "online_presence", "naam", "stad", "niche", "telefoon", 
                "eigen_score", "sterren", "aantal_reviews", "maps_url", 
                "gebeld", "call_result", "notes"
            ],
            column_config={
                "is_deleted": st.column_config.CheckboxColumn(
                    "❌ Archive?",
                    help="Check to move this lead to the archive",
                    default=False
                ),
                "online_presence": st.column_config.SelectboxColumn(
                    "Online Presence / Status",
                    help="Set online presence or business operating status",
                    options=[
                        "-",
                        "❌ Neither Website nor Profile",
                        "🌐 Has Website, No Social Profile",
                        "👤 Has Profile, No Website",
                        "✔️ Both Present",
                        "⏳ Temporarily Closed",
                        "⛔ Permanently Closed"
                    ]
                ),
                "naam": st.column_config.TextColumn("Company Name", disabled=True),
                "stad": st.column_config.TextColumn("City", disabled=True),
                "niche": st.column_config.TextColumn("Niche", disabled=True),
                "telefoon": st.column_config.TextColumn("Phone", disabled=True),
                "eigen_score": st.column_config.NumberColumn(
                    "Score (0-100)",
                    min_value=0,
                    max_value=100,
                    step=5
                ),
                "sterren": st.column_config.NumberColumn(
                    "Rating",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    format="%.1f ⭐"
                ),
                "aantal_reviews": st.column_config.NumberColumn(
                    "Reviews",
                    min_value=0,
                    step=1
                ),
                "maps_url": st.column_config.LinkColumn(
                    "📍 Maps",
                    display_text="Open Maps"
                ),
                "gebeld": st.column_config.CheckboxColumn("Called?"),
                "call_result": st.column_config.SelectboxColumn(
                    "Call Status",
                    options=["-", "✔️ Deal / Interest", "❌ No interest", "➖ No answer / Callback"]
                ),
                "notes": st.column_config.TextColumn("Notes")
            },
            disabled=["id", "naam", "stad", "niche", "telefoon", "adres", "status", "gecheckt_op", "maps_url"],
            hide_index=True,
            use_container_width=True,
            key="leads_editor"
        )

        if st.button("💾 Save Changes"):
            conn = get_db_connection()
            cursor = conn.cursor()
            for idx, row in edited_df.iterrows():
                gebeld_val = 1 if row["gebeld"] else 0
                deleted_val = 1 if row["is_deleted"] else 0
                cursor.execute("""
                    UPDATE leads 
                    SET gebeld = ?, call_result = ?, notes = ?, sterren = ?, aantal_reviews = ?, eigen_score = ?, is_deleted = ?, online_presence = ?
                    WHERE id = ?
                """, (gebeld_val, row["call_result"], row["notes"], row["sterren"], row["aantal_reviews"], row["eigen_score"], deleted_val, row["online_presence"], row["id"]))
            conn.commit()
            conn.close()
            st.success("Changes saved successfully!")
            st.rerun()

        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Selection to CSV",
            data=csv,
            file_name="leads_export.csv",
            mime="text/csv"
        )

elif page_selection == "🗑️ Closed / Archived":
    st.title("🗑️ Archived & Closed Leads")
    st.caption("Manage archived leads and filter by online presence or closure status.")

    conn = get_db_connection()
    df_deleted = pd.read_sql_query("SELECT * FROM leads WHERE is_deleted = 1 ORDER BY id DESC", conn)
    conn.close()

    if df_deleted.empty:
        st.info("No archived leads found.")
    else:
        df_deleted["is_deleted"] = df_deleted["is_deleted"].astype(bool)

        presence_options = ["All Statuses"] + sorted(list(set(df_deleted["online_presence"].dropna().tolist())))
        selected_presence = st.selectbox("🔍 Filter Archive by Status:", presence_options)

        filtered_deleted_df = df_deleted.copy()
        if selected_presence != "All Statuses":
            filtered_deleted_df = filtered_deleted_df[filtered_deleted_df["online_presence"] == selected_presence]

        st.write(f"Archived leads displayed: **{len(filtered_deleted_df)}**")

        edited_deleted_df = st.data_editor(
            filtered_deleted_df,
            column_order=["is_deleted", "online_presence", "naam", "stad", "niche", "telefoon", "notes"],
            column_config={
                "is_deleted": st.column_config.CheckboxColumn(
                    "Archived?",
                    help="Uncheck to restore this lead back to the main dashboard"
                ),
                "online_presence": st.column_config.SelectboxColumn(
                    "Online Presence / Status",
                    options=[
                        "-",
                        "❌ Neither Website nor Profile",
                        "🌐 Has Website, No Social Profile",
                        "👤 Has Profile, No Website",
                        "✔️ Both Present",
                        "⏳ Temporarily Closed",
                        "⛔ Permanently Closed"
                    ]
                ),
                "naam": st.column_config.TextColumn("Company Name", disabled=True),
                "stad": st.column_config.TextColumn("City", disabled=True),
                "niche": st.column_config.TextColumn("Niche", disabled=True),
                "telefoon": st.column_config.TextColumn("Phone", disabled=True),
                "notes": st.column_config.TextColumn("Notes")
            },
            disabled=["id", "naam", "stad", "niche", "telefoon", "adres", "status", "gecheckt_op", "maps_url", "sterren", "aantal_reviews", "eigen_score", "gebeld", "call_result"],
            hide_index=True,
            use_container_width=True,
            key="deleted_editor"
        )

        if st.button("💾 Save Archive Changes"):
            conn = get_db_connection()
            cursor = conn.cursor()
            for idx, row in edited_deleted_df.iterrows():
                deleted_val = 1 if row["is_deleted"] else 0
                cursor.execute("""
                    UPDATE leads 
                    SET is_deleted = ?, online_presence = ?, notes = ?
                    WHERE id = ?
                """, (deleted_val, row["online_presence"], row["notes"], row["id"]))
            conn.commit()
            conn.close()
            st.success("Archive updated successfully!")
            st.rerun()

elif page_selection == "⚙️ Niches & Cities":
    st.title("⚙️ Search Configuration")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Target Cities")
        new_city = st.text_input("Add new city:")
        if st.button("➕ Add City"):
            if new_city.strip():
                formatted_city = new_city.strip().capitalize()
                if formatted_city not in cities:
                    cities.append(formatted_city)
                    save_json(CITIES_PATH, cities)
                    st.success(f"City '{formatted_city}' added!")
                    st.rerun()

        st.write(", ".join(cities))

    with col2:
        st.subheader("🛠️ Target Niches (OSM Tags)")
        new_niche = st.text_input("Add new niche:")
        if st.button("➕ Add Niche"):
            if new_niche.strip():
                formatted_niche = new_niche.strip().lower()
                if formatted_niche not in niches:
                    niches.append(formatted_niche)
                    save_json(NICHES_PATH, niches)
                    st.success(f"Niche '{formatted_niche}' added!")
                    st.rerun()

        st.write(", ".join(niches))
