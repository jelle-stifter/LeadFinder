import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import pandas as pd
import subprocess
import json
import os
import urllib.parse
import math
from datetime import datetime

st.set_page_config(
    page_title="LeadFinder Pro | Enterprise CRM", 
    layout="wide", 
    page_icon="⚡", 
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0b0f17;
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20px;
        margin-bottom: 20px;
        border-bottom: 1px solid #1e2638;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .header-subtitle {
        font-size: 0.88rem;
        color: #8a94a6;
        margin-top: 2px;
    }

    [data-testid="stMetric"] {
        background: #131a29;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #1e2638;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #3b82f6;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        font-feature-settings: "zero" 1;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    div[data-testid="stSidebarNav"] {display: none;}
    section[data-testid="stSidebar"] {
        background-color: #0d121d;
        border-right: 1px solid #1e2638;
        padding-top: 10px;
    }
    .brand-box {
        padding: 10px 15px 20px 15px;
        border-bottom: 1px solid #1e2638;
        margin-bottom: 15px;
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .brand-badge {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: #ffffff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: 6px;
    }

    div[data-testid="stDataEditor"] {
        border: 1px solid #1e2638;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background: #2563eb;
        border: none;
        color: #ffffff;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #1d4ed8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .btn-highprio > button {
        background-color: #10b981 !important;
        font-size: 0.9rem !important;
        padding: 15px 5px !important;
    }
    .btn-highprio > button:hover {
        background-color: #059669 !important;
    }
    .btn-medprio > button {
        background-color: #06b6d4 !important;
        font-size: 0.9rem !important;
        padding: 15px 5px !important;
    }
    .btn-medprio > button:hover {
        background-color: #0891b2 !important;
    }
    .btn-archive > button {
        background-color: #ef4444 !important;
        font-size: 0.9rem !important;
        padding: 15px 5px !important;
    }
    .btn-archive > button:hover {
        background-color: #dc2626 !important;
    }
    .btn-closed > button {
        background-color: #4b5563 !important;
        font-size: 0.9rem !important;
        padding: 15px 5px !important;
    }
    .btn-closed > button:hover {
        background-color: #374151 !important;
    }
    .btn-skip > button {
        background-color: #f59e0b !important;
        font-size: 0.9rem !important;
        padding: 15px 5px !important;
    }
    .btn-skip > button:hover {
        background-color: #d97706 !important;
    }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "/home/jelle/leadfinder/leads.db"
CITIES_PATH = "/home/jelle/leadfinder/cities.json"
NICHES_PATH = "/home/jelle/leadfinder/niches.json"
LOG_PATH = "/home/jelle/leadfinder/worker.log"
PROGRESS_PATH = "/home/jelle/leadfinder/progress.json"

CITY_COORDINATES = {
    "Maasmechelen": (50.9634, 5.6942), "Genk": (50.9650, 5.5002), "Hasselt": (50.9311, 5.3378),
    "Lanaken": (50.8911, 5.6496), "Dilsen-Stokkem": (51.0319, 5.7197), "Bree": (51.1417, 5.5973),
    "Zutendaal": (50.9324, 5.5721), "Bilzen": (50.8706, 5.5168), "Tongeren": (50.7806, 5.4644),
    "Oudsbergen": (51.0483, 5.6008), "Pelt": (51.2131, 5.4269), "Lommel": (51.2306, 5.3044),
    "Sint-Truiden": (50.8153, 5.1864), "Beringen": (51.0494, 5.2269), "Diepenbeek": (50.9083, 5.4172),
    "Heusden-Zolder": (51.0381, 5.2778), "Halen": (50.9483, 5.1172), "Tessenderlo": (51.0683, 5.0872),
    "Leopoldsburg": (51.1183, 5.2572), "Peer": (51.1342, 5.4544), "Hamont-Achel": (51.2500, 5.5500),
    "Voeren": (50.7683, 5.7472), "Riemst": (50.8111, 5.5981), "Leuven": (50.8798, 4.7005),
    "Diest": (50.9847, 5.0514), "Aarschot": (50.9858, 4.8361), "Tienen": (50.8075, 4.9378),
    "Turnhout": (51.3225, 4.9447), "Geel": (51.1611, 4.9903), "Mol": (51.1911, 5.1169),
    "Herentals": (51.1764, 4.8344), "Mechelen": (51.0257, 4.4778), "Antwerpen": (51.2194, 4.4025),
    "Sittard": (50.9983, 5.8661), "Geleen": (50.9710, 5.8278), "Maastricht": (50.8514, 5.6910),
    "Eindhoven": (51.4416, 5.4697), "Roermond": (51.1942, 5.9875), "Weert": (51.2517, 5.7069),
    "Heerlen": (50.8882, 5.9794), "Breda": (51.5719, 4.7683), "Tilburg": (51.5606, 5.0919)
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return sorted(data, key=lambda x: str(x).lower())
                return data
        except Exception:
            return sorted(default, key=lambda x: str(x).lower()) if isinstance(default, list) else default
    return sorted(default, key=lambda x: str(x).lower()) if isinstance(default, list) else default

def save_json(path, data):
    if isinstance(data, list):
        data = sorted(data, key=lambda x: str(x).lower())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn

def is_worker_running():
    try:
        output = subprocess.check_output(["ps", "aux"]).decode()
        return "worker.py" in output
    except Exception:
        return False

def get_last_logs(n_lines=30):
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[-n_lines:])
        except Exception:
            return "Error reading log file."
    return "No log file found."

conn = get_db_connection()
c = conn.cursor()
try:
    c.execute("ALTER TABLE leads ADD COLUMN verification_status TEXT DEFAULT 'Unverified'")
except sqlite3.OperationalError:
    pass
try:
    c.execute("ALTER TABLE leads ADD COLUMN last_called_at TEXT")
except sqlite3.OperationalError:
    pass
try:
    c.execute("ALTER TABLE leads ADD COLUMN priority_level TEXT DEFAULT 'LOW'")
except sqlite3.OperationalError:
    pass
conn.commit()
conn.close()

with st.sidebar:
    st.markdown("""
        <div class="brand-box">
            <span class="brand-title">LeadFinder</span>
            <span class="brand-badge">PRO</span>
        </div>
    """, unsafe_allow_html=True)
    
    if is_worker_running():
        st.success("🟢 Engine Active")
    else:
        st.error("🔴 Engine Stopped")

    page_selection = option_menu(
        menu_title=None,
        options=[
            "Main Database", 
            "Quick Manual Check",
            "Call Center",
            "Verification Scanner",
            "Management & Entry",
            "Live Activity Control"
        ],
        icons=[
            "database-fill", 
            "lightning-charge-fill",
            "telephone-outbound-fill", 
            "shield-check",
            "gear-fill", 
            "cpu-fill"
        ],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "0.95rem"},
            "nav-link": {
                "font-size": "0.88rem",
                "text-align": "left",
                "margin": "4px 0px",
                "padding": "10px 14px",
                "border-radius": "8px",
                "color": "#94a3b8",
                "font-weight": "500",
                "--hover-color": "#1e293b"
            },
            "nav-link-selected": {
                "background-color": "#1e293b",
                "color": "#38bdf8",
                "font-weight": "600",
                "border-left": "3px solid #38bdf8"
            }
        }
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Sync & Refresh", width="stretch"):
        st.rerun()

st.markdown("""
    <div class="header-container">
        <div>
            <div class="header-title">B2B Lead Intelligence Dashboard</div>
            <div class="header-subtitle">Real-time prospect tracking, geo-radius filtering & domain verification</div>
        </div>
    </div>
""", unsafe_allow_html=True)

conn = get_db_connection()
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM leads WHERE is_deleted = 0 OR is_deleted IS NULL")
total_leads = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM leads WHERE need_to_call = 1 AND (gebeld = 0 OR gebeld IS NULL) AND (is_deleted = 0 OR is_deleted IS NULL)")
total_queue = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM leads WHERE gebeld = 1 AND (is_deleted = 0 OR is_deleted IS NULL)")
total_called = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM leads WHERE priority_level = 'HIGH' AND need_to_call = 1 AND (gebeld = 0 OR gebeld IS NULL) AND (is_deleted = 0 OR is_deleted IS NULL)")
total_high_prio = c.fetchone()[0]
conn.close()

m1, m2, m3, m4 = st.columns(4)
m1.metric("📦 Total Active Leads", total_leads)
m2.metric("📞 Total Call Queue", total_queue)
m3.metric("🔥 High Prio (No Site + No Profile)", total_high_prio)
m4.metric("✅ Completed Calls", total_called)

st.markdown("<br>", unsafe_allow_html=True)

def render_lead_table(query, params=(), table_key="default"):
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        st.info("No records matching the selected parameters.")
        return

    defaults = {
        "gebeld": 0, "call_result": "-", "notes": "",
        "maps_url": "", "is_deleted": 0, "need_to_call": 0, "verification_status": "Unverified", "priority_level": "LOW"
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val

    df["gebeld"] = df["gebeld"].astype(bool)
    df["is_deleted"] = df["is_deleted"].astype(bool)
    df["need_to_call"] = df["need_to_call"].astype(bool)

    df["maps_search_url"] = df.apply(
        lambda r: f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(r['naam']) + ' ' + str(r['stad']))}", 
        axis=1
    )

    with st.expander("🔍 **Filter Engine & Radius Targeting**", expanded=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            all_cities = ["All Cities"] + sorted(list(set(df["stad"].dropna().tolist())), key=lambda x: x.lower())
            selected_city = st.selectbox("📍 Target City:", all_cities, key=f"city_{table_key}")

        with f_col2:
            all_niches = ["All Niches"] + sorted(list(set(df["niche"].dropna().tolist())), key=lambda x: x.lower())
            selected_niche = st.selectbox("🛠️ Target Niche:", all_niches, key=f"niche_{table_key}")

        with f_col3:
            phone_filter = st.selectbox(
                "📱 Phone Availability:",
                ["All Leads", "With Phone Number Only", "Without Phone Number Only"],
                key=f"phone_{table_key}"
            )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            sorted_center_cities = sorted(list(CITY_COORDINATES.keys()), key=lambda x: x.lower())
            center_city = st.selectbox("🎯 Geo-Center City:", ["None"] + sorted_center_cities, key=f"center_{table_key}")

        with r_col2:
            max_radius = st.slider("Target Radius (km):", 5, 150, 30, step=5, key=f"rad_{table_key}")

    filtered_df = df.copy()

    if selected_city != "All Cities":
        filtered_df = filtered_df[filtered_df["stad"] == selected_city]
    if selected_niche != "All Niches":
        filtered_df = filtered_df[filtered_df["niche"] == selected_niche]

    if phone_filter == "With Phone Number Only":
        filtered_df = filtered_df[(filtered_df["telefoon"].str.strip() != "No phone") & (filtered_df["telefoon"].str.strip() != "")]
    elif phone_filter == "Without Phone Number Only":
        filtered_df = filtered_df[(filtered_df["telefoon"].str.strip() == "No phone") | (filtered_df["telefoon"].str.strip() == "")]

    if center_city != "None" and center_city in CITY_COORDINATES:
        lat_c, lon_c = CITY_COORDINATES[center_city]
        
        def calculate_lead_distance(city_name):
            if city_name in CITY_COORDINATES:
                lat_l, lon_l = CITY_COORDINATES[city_name]
                return haversine_distance(lat_c, lon_c, lat_l, lon_l)
            return 9999.0

        filtered_df["distance_km"] = filtered_df["stad"].apply(calculate_lead_distance)
        filtered_df = filtered_df[filtered_df["distance_km"] <= max_radius]
        filtered_df["distance_km"] = filtered_df["distance_km"].round(1)

    st.markdown(f"Displaying **{len(filtered_df)}** verified prospects")

    column_order_list = [
        "need_to_call", "priority_level", "verification_status", "naam", "stad", "niche", "telefoon", 
        "maps_url", "maps_search_url", "notes", "is_deleted"
    ]
    if center_city != "None":
        column_order_list.insert(6, "distance_km")

    edited_df = st.data_editor(
        filtered_df,
        column_order=column_order_list,
        column_config={
            "need_to_call": st.column_config.CheckboxColumn("📞 Queue?", default=False),
            "priority_level": st.column_config.TextColumn("Prio"),
            "verification_status": st.column_config.TextColumn("Status / Theme"),
            "naam": st.column_config.TextColumn("Company Name"),
            "stad": st.column_config.TextColumn("Location"),
            "niche": st.column_config.TextColumn("Niche"),
            "telefoon": st.column_config.TextColumn("Phone Number"),
            "maps_url": st.column_config.TextColumn("Exact Maps URL"),
            "maps_search_url": st.column_config.LinkColumn("🔍 Direct Search", display_text="Open Map"),
            "notes": st.column_config.TextColumn("Activity Notes"),
            "is_deleted": st.column_config.CheckboxColumn("🗑️ Archive?", default=False),
            "distance_km": st.column_config.NumberColumn("Distance", format="%.1f km")
        },
        disabled=["id", "verification_status", "priority_level", "maps_search_url", "distance_km"],
        hide_index=True,
        width="stretch",
        key=f"editor_{table_key}"
    )

    if st.button("💾 Apply & Commit Changes", key=f"btn_save_{table_key}", type="primary"):
        conn = get_db_connection()
        cursor = conn.cursor()
        for idx, row in edited_df.iterrows():
            deleted_val = 1 if row["is_deleted"] else 0
            need_call_val = 1 if row["need_to_call"] else 0
            cursor.execute("""
                UPDATE leads 
                SET naam = ?, stad = ?, niche = ?, telefoon = ?, maps_url = ?, notes = ?, is_deleted = ?, need_to_call = ?
                WHERE id = ?
            """, (row["naam"], row["stad"], row["niche"], row["telefoon"], row["maps_url"], row["notes"], deleted_val, need_call_val, row["id"]))
        conn.commit()
        conn.close()
        st.success("Database records synchronized successfully!")
        st.rerun()

# Router Logic
if page_selection == "Main Database":
    st.subheader("📊 Main Prospects Repository")
    query = "SELECT * FROM leads WHERE (is_deleted = 0 OR is_deleted IS NULL) ORDER BY id DESC"
    render_lead_table(query, table_key="main_db")

elif page_selection == "Quick Manual Check":
    st.subheader("⚡ Quick Manual Check")
    st.caption("Classify leads: Has Website, Has Profile or Closed are archived. Missing features send lead to Call Queue.")

    conn = get_db_connection()
    df_unverified = pd.read_sql_query("""
        SELECT id, naam, stad, niche, telefoon, verification_status, notes, maps_url 
        FROM leads 
        WHERE (is_deleted = 0 OR is_deleted IS NULL) AND need_to_call = 0
    """, conn)
    conn.close()

    if df_unverified.empty:
        st.success("🎉 All active leads have been processed or moved to the call queue!")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            all_qc_cities = ["All Cities"] + sorted(list(set(df_unverified["stad"].dropna().tolist())), key=lambda x: x.lower())
            qc_selected_city = st.selectbox("📍 Filter City:", all_qc_cities, key="qc_city_filter")
        with col_f2:
            all_qc_niches = ["All Niches"] + sorted(list(set(df_unverified["niche"].dropna().tolist())), key=lambda x: x.lower())
            qc_selected_niche = st.selectbox("🛠️ Filter Niche:", all_qc_niches, key="qc_niche_filter")

        filtered_qc_df = df_unverified.copy()
        if qc_selected_city != "All Cities":
            filtered_qc_df = filtered_qc_df[filtered_qc_df["stad"] == qc_selected_city]
        if qc_selected_niche != "All Niches":
            filtered_qc_df = filtered_qc_df[filtered_qc_df["niche"] == qc_selected_niche]

        if filtered_qc_df.empty:
            st.warning("No unverified leads matching the selected City and Niche filters.")
        else:
            st.markdown(f"**{len(filtered_qc_df)}** leads remaining in this filtered verification queue.")
            
            current_lead = filtered_qc_df.iloc[0]
            lead_id = int(current_lead["id"])
            name = current_lead["naam"]
            city = current_lead["stad"]
            niche = current_lead["niche"]
            phone = current_lead["telefoon"]
            ver_status = current_lead["verification_status"]
            current_notes = current_lead["notes"] if current_lead["notes"] else ""
            maps_url = current_lead["maps_url"]

            maps_search_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(str(name) + ' ' + str(city))}"
            target_maps_link = maps_url if maps_url and str(maps_url).strip() else maps_search_url

            st.markdown(f"""
                <div style="background: #131a29; padding: 25px; border-radius: 12px; border: 1px solid #1e2638; margin-bottom: 20px;">
                    <h1 style="color: #ffffff; margin-bottom: 5px;">🏢 {name}</h1>
                    <h4 style="color: #8a94a6; margin-top: 0;">📍 {city} &nbsp;|&nbsp; 🛠️ Niche: <span style="color: #38bdf8;">{niche}</span> &nbsp;|&nbsp; 📱 Tel: <span style="color: #10b981;">{phone}</span></h4>
                    <p style="color: #64748b; font-size: 0.9rem;">Auto DNS Status: <strong>{ver_status}</strong></p>
                    <hr style="border-color: #1e2638; margin: 15px 0;">
                    <a href="{target_maps_link}" target="_blank" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 1.1rem;">
                        🗺️ Open in Google Maps ↗
                    </a>
                </div>
            """, unsafe_allow_html=True)

            with st.expander("📝 **Add / Edit Notes for this Lead**", expanded=False):
                with st.form(f"qc_notes_form_{lead_id}"):
                    new_note = st.text_area("Lead Notes", value=current_notes, height=100)
                    save_note_btn = st.form_submit_button("💾 Save Notes", type="primary")
                    if save_note_btn:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("UPDATE leads SET notes = ? WHERE id = ?", (new_note.strip(), lead_id))
                        conn.commit()
                        conn.close()
                        st.success("Note saved successfully!")
                        st.rerun()

            col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)

            with col_a:
                st.markdown('<div class="btn-highprio">', unsafe_allow_html=True)
                if st.button("🔥 NO SITE &\nNO PROFILE\n(PRIO CALL)", width="stretch", key="qc_nosite_noprof"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE leads 
                        SET need_to_call = 1, verification_status = 'No Site & No Profile', priority_level = 'HIGH' 
                        WHERE id = ?
                    """, (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_b:
                st.markdown('<div class="btn-medprio">', unsafe_allow_html=True)
                if st.button("🟠 NO SITE ONLY\n(ADD TO CALLS)", width="stretch", key="qc_nosite"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE leads 
                        SET need_to_call = 1, verification_status = 'No Website Only', priority_level = 'MEDIUM' 
                        WHERE id = ?
                    """, (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_c:
                st.markdown('<div class="btn-medprio">', unsafe_allow_html=True)
                if st.button("🔵 NO PROFILE ONLY\n(ADD TO CALLS)", width="stretch", key="qc_noprof"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE leads 
                        SET need_to_call = 1, verification_status = 'No Profile Only', priority_level = 'LOW' 
                        WHERE id = ?
                    """, (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_d:
                st.markdown('<div class="btn-archive">', unsafe_allow_html=True)
                if st.button("🔴 HAS SITE OR\nHAS PROFILE\n(ARCHIVE)", width="stretch", key="qc_hasweb"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE leads 
                        SET is_deleted = 1, verification_status = 'Has Website/Profile', need_to_call = 0 
                        WHERE id = ?
                    """, (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_e:
                st.markdown('<div class="btn-closed">', unsafe_allow_html=True)
                if st.button("⬛ PERMANENTLY\nCLOSED\n(ARCHIVE)", width="stretch", key="qc_closed"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        UPDATE leads 
                        SET is_deleted = 1, verification_status = 'Permanently Closed', need_to_call = 0 
                        WHERE id = ?
                    """, (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_f:
                st.markdown('<div class="btn-skip">', unsafe_allow_html=True)
                if st.button("🟡 NOT SURE\n(SKIP)", width="stretch", key="qc_skip"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("UPDATE leads SET id = (SELECT MIN(id) - 1 FROM leads) WHERE id = ?", (lead_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif page_selection == "Call Center":
    st.subheader("📞 Call Center Workbench")

    tab_queue, tab_history = st.tabs(["📋 Active Call Queue", "✅ Call History & Outcomes"])

    with tab_queue:
        st.markdown("##### Prospects Marked for Calling (Prioritized)")
        conn = get_db_connection()
        df_queue = pd.read_sql_query("""
            SELECT id, naam, stad, niche, telefoon, verification_status, priority_level, notes, maps_url 
            FROM leads 
            WHERE need_to_call = 1 AND (gebeld = 0 OR gebeld IS NULL) AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY 
                CASE priority_level 
                    WHEN 'HIGH' THEN 1 
                    WHEN 'MEDIUM' THEN 2 
                    ELSE 3 
                END ASC, id DESC
        """, conn)
        conn.close()

        if df_queue.empty:
            st.info("The call queue is currently empty. Add leads to the queue via Main Database or Quick Check.")
        else:
            col_sel, col_action = st.columns([1, 2])
            
            with col_sel:
                def get_prio_label(row):
                    prio_prefix = "🔥 HIGH PRIO: " if row['priority_level'] == 'HIGH' else ""
                    return f"{prio_prefix}{row['naam']} ({row['stad']}) - [{row['verification_status']}]"

                lead_options = {get_prio_label(row): row['id'] for _, row in df_queue.iterrows()}
                selected_label = st.selectbox("🎯 Select Lead to Call:", list(lead_options.keys()))
                selected_id = lead_options[selected_label]
                
                selected_lead = df_queue[df_queue['id'] == selected_id].iloc[0]

            with col_action:
                st.markdown(f"### 🏢 {selected_lead['naam']}")
                
                prio_badge = "🔥 **HIGH PRIORITY (No Site & No Profile)**" if selected_lead['priority_level'] == 'HIGH' else f"Priority: {selected_lead['priority_level']}"
                st.markdown(prio_badge)
                
                st.write(f"📍 **Location:** {selected_lead['stad']} | 🛠️ **Niche:** {selected_lead['niche']}")
                st.write(f"📱 **Phone:** `{selected_lead['telefoon']}` | 🏷️ **Main Problem / Theme:** `{selected_lead['verification_status']}`")
                
                if selected_lead['maps_url']:
                    st.markdown(f"[🔗 Google Maps Link]({selected_lead['maps_url']})")

                with st.form(f"call_log_form_{selected_id}", clear_on_submit=True):
                    call_result = st.selectbox("Call Outcome *", [
                        "Interested - Send Proposal",
                        "Interested - Schedule Follow-up",
                        "No Interest",
                        "No Answer / Voicemail",
                        "Invalid Number / Wrong Contact",
                        "Already Has Website"
                    ])
                    call_notes = st.text_area("Call Notes / Feedback", value=selected_lead['notes'] if selected_lead['notes'] else "")
                    
                    btn_submit = st.form_submit_button("💾 Save Call Log & Complete", type="primary")

                    if btn_submit:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""
                            UPDATE leads 
                            SET gebeld = 1, call_result = ?, notes = ?, last_called_at = ?, need_to_call = 0
                            WHERE id = ?
                        """, (call_result, call_notes, timestamp, selected_id))
                        conn.commit()
                        conn.close()
                        st.success(f"Call log for '{selected_lead['naam']}' saved successfully!")
                        st.rerun()

            st.markdown("---")
            st.markdown("##### Full Pending Call Queue List")
            st.dataframe(
                df_queue[['priority_level', 'verification_status', 'naam', 'stad', 'niche', 'telefoon', 'notes']], 
                width="stretch", 
                hide_index=True
            )

    with tab_history:
        st.markdown("##### Completed Call Logs")
        conn = get_db_connection()
        df_history = pd.read_sql_query("""
            SELECT id, naam, stad, niche, telefoon, call_result, notes, last_called_at 
            FROM leads 
            WHERE gebeld = 1 AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY last_called_at DESC, id DESC
        """, conn)
        conn.close()

        if df_history.empty:
            st.info("No calls logged yet.")
        else:
            st.dataframe(
                df_history, 
                column_config={
                    "naam": "Company Name",
                    "stad": "City",
                    "niche": "Niche",
                    "telefoon": "Phone",
                    "call_result": "Outcome",
                    "notes": "Call Notes",
                    "last_called_at": "Call Date/Time"
                },
                width="stretch", 
                hide_index=True
            )

elif page_selection == "Verification Scanner":
    st.subheader("🛡️ Automated Web Domain Verification")
    
    col_scan_info, col_scan_btn = st.columns([3, 1])
    with col_scan_info:
        st.caption("Verifies active DNS web records (.be / .nl) for each company name without paid API dependencies.")
    with col_scan_btn:
        if st.button("⚡ Run Domain Verification", type="primary", width="stretch"):
            with st.spinner("Scanning DNS records for all leads..."):
                try:
                    subprocess.run(["python3", "/home/jelle/leadfinder/verify_leads.py"], check=True)
                    st.success("Domain verification complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error running verification: {e}")

    with st.expander("⚠️ **Mark Lead as 'Has Website' & Archive**", expanded=False):
        conn = get_db_connection()
        df_all_active = pd.read_sql_query("SELECT id, naam, stad FROM leads WHERE (is_deleted = 0 OR is_deleted IS NULL) ORDER BY naam ASC", conn)
        conn.close()

        if not df_all_active.empty:
            override_options = {f"{row['naam']} ({row['stad']})": row['id'] for _, row in df_all_active.iterrows()}
            sel_lead_label = st.selectbox("Select lead that actually HAS a website:", list(override_options.keys()))
            sel_lead_id = override_options[sel_lead_label]

            if st.button("🗑️ Mark 'Has Website' & Archive Lead", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("UPDATE leads SET verification_status = 'Has Website', is_deleted = 1, need_to_call = 0 WHERE id = ?", (sel_lead_id,))
                conn.commit()
                conn.close()
                st.success(f"Lead marked as 'Has Website' and moved to archive!")
                st.rerun()

    tab_no_web, tab_potential = st.tabs(["✅ No Website Confirmed", "⚠️ Potential Website / Ambiguous"])

    with tab_no_web:
        query = "SELECT * FROM leads WHERE verification_status = 'No Website' AND (is_deleted = 0 OR is_deleted IS NULL) ORDER BY id DESC"
        render_lead_table(query, table_key="tab_no_web")

    with tab_potential:
        query = "SELECT * FROM leads WHERE verification_status = 'Potential Website' AND (is_deleted = 0 OR is_deleted IS NULL) ORDER BY id DESC"
        render_lead_table(query, table_key="tab_potential")

elif page_selection == "Management & Entry":
    st.subheader("⚙️ System Management & Manual Lead Injection")
    
    with st.expander("➕ **Inject Prospect Manually**", expanded=True):
        with st.form("manual_lead_form", clear_on_submit=True):
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                m_name = st.text_input("Company Name *")
                m_city = st.text_input("City *")
                m_niche = st.text_input("Niche / Category", value="general")
            with m_col2:
                m_phone = st.text_input("Phone Number", value="No phone")
                m_maps = st.text_input("Exact Maps URL (optional)")
                m_notes = st.text_input("Notes")

            submit_lead = st.form_submit_button("➕ Commit Lead to Database", type="primary")

            if submit_lead:
                if not m_name.strip() or not m_city.strip():
                    st.error("Company Name and City are required fields.")
                else:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO leads (naam, stad, niche, telefoon, adres, maps_url, sterren, aantal_reviews, eigen_score, gebeld, call_result, notes, is_deleted, online_presence, need_to_call, verification_status, priority_level)
                        VALUES (?, ?, ?, ?, ?, ?, 0.0, 0, 50, 0, '-', ?, 0, '-', 0, 'Unverified', 'LOW')
                    """, (m_name.strip(), m_city.strip().capitalize(), m_niche.strip().lower(), m_phone.strip(), m_city.strip(), m_maps.strip(), m_notes.strip()))
                    conn.commit()
                    conn.close()
                    st.success(f"Prospect **'{m_name}'** successfully added!")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚙️ Target Configurations Management")

    cities_list = load_json(CITIES_PATH, ["Maasmechelen"])
    niches_list = load_json(NICHES_PATH, ["Schrijnwerker"])

    cfg_col1, cfg_col2 = st.columns(2)

    with cfg_col1:
        st.markdown("##### 📍 Target Cities Config")
        st.caption(f"Currently active cities: **{len(cities_list)}**")

        new_city = st.text_input("Add new target city:", key="input_new_city")
        if st.button("➕ Add City", key="btn_add_city"):
            if new_city.strip():
                formatted_city = new_city.strip().capitalize()
                if formatted_city not in cities_list:
                    cities_list.append(formatted_city)
                    save_json(CITIES_PATH, cities_list)
                    st.success(f"City '{formatted_city}' added to configuration!")
                    st.rerun()

        st.markdown("---")
        cities_to_remove = st.multiselect("Select cities to remove:", options=cities_list, key="multiselect_remove_cities")
        if st.button("🗑️ Remove Selected Cities", key="btn_remove_cities"):
            if cities_to_remove:
                updated_cities = [c for c in cities_list if c not in cities_to_remove]
                save_json(CITIES_PATH, updated_cities)
                st.success("Selected cities removed!")
                st.rerun()

        st.markdown("**Active Cities List (Alphabetical):**")
        st.dataframe(pd.DataFrame(cities_list, columns=["City Name"]), width="stretch", height=220)

    with cfg_col2:
        st.markdown("##### 🛠️ Target Niches Config")
        st.caption(f"Currently active niches: **{len(niches_list)}**")

        new_niche = st.text_input("Add new target niche:", key="input_new_niche")
        if st.button("➕ Add Niche", key="btn_add_niche"):
            if new_niche.strip():
                formatted_niche = new_niche.strip()
                if formatted_niche not in niches_list:
                    niches_list.append(formatted_niche)
                    save_json(NICHES_PATH, niches_list)
                    st.success(f"Niche '{formatted_niche}' added to configuration!")
                    st.rerun()

        st.markdown("---")
        niches_to_remove = st.multiselect("Select niches to remove:", options=niches_list, key="multiselect_remove_niches")
        if st.button("🗑️ Remove Selected Niches", key="btn_remove_niches"):
            if niches_to_remove:
                updated_niches = [n for n in niches_list if n not in niches_to_remove]
                save_json(NICHES_PATH, updated_niches)
                st.success("Selected niches removed!")
                st.rerun()

        st.markdown("**Active Niches List (Alphabetical):**")
        st.dataframe(pd.DataFrame(niches_list, columns=["Niche Name"]), width="stretch", height=220)

elif page_selection == "Live Activity Control":
    st.subheader("📡 System Diagnostics & Worker State")
    
    prog_data = load_json(PROGRESS_PATH, {"last_city_index": 0, "last_niche_index": 0})
    cities_list = load_json(CITIES_PATH, ["Maasmechelen"])
    niches_list = load_json(NICHES_PATH, ["Schrijnwerker"])

    c_curr = min(prog_data.get("last_city_index", 0), len(cities_list)-1) if cities_list else 0
    n_curr = min(prog_data.get("last_niche_index", 0), len(niches_list)-1) if niches_list else 0

    curr_city_name = cities_list[c_curr] if cities_list else "-"
    curr_niche_name = niches_list[n_curr] if niches_list else "-"

    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"📍 **Target City State:** {curr_city_name} ({c_curr+1}/{len(cities_list)})")
    with col_b:
        st.info(f"🛠️ **Target Niche State:** {curr_niche_name} ({n_curr+1}/{len(niches_list)})")

    if st.button("⚠️ Reset Crawler State Index"):
        save_json(PROGRESS_PATH, {"last_city_index": 0, "last_niche_index": 0})
        st.success("Crawler index reset to 0!")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Crawler Log Terminal Output")
    st.code(get_last_logs(35), language="text")
