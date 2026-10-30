import sqlite3
import requests
import json
import time
import os
import logging
import urllib.parse
from duckduckgo_search import DDGS

logging.basicConfig(
    filename='/home/jelle/leadfinder/worker.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

DB_PATH = "/home/jelle/leadfinder/leads.db"
CITIES_PATH = "/home/jelle/leadfinder/cities.json"
NICHES_PATH = "/home/jelle/leadfinder/niches.json"

DEFAULT_CITIES = ["Maasmechelen", "Genk", "Hasselt"]
DEFAULT_NICHES = ["carpenter", "tiler", "painter", "electrician", "plumber"]

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT,
            telefoon TEXT,
            adres TEXT,
            stad TEXT,
            niche TEXT,
            status TEXT DEFAULT 'nieuw',
            gecheckt_op TEXT,
            gebeld INTEGER DEFAULT 0,
            call_result TEXT DEFAULT '-',
            notes TEXT DEFAULT '',
            maps_url TEXT DEFAULT '',
            sterren REAL DEFAULT 0.0,
            aantal_reviews INTEGER DEFAULT 0,
            eigen_score INTEGER DEFAULT 50,
            UNIQUE(naam, stad)
        )
    ''')
    conn.commit()
    conn.close()

def get_osm_data(city, niche_type):
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    headers = {"User-Agent": "LeadFinderWorker/1.0 (contact@leadfinder.local)"}
    
    try:
        nom_url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(city)},Belgium"
        res = requests.get(nom_url, headers=headers, timeout=10).json()
        if not res:
            return []
        lat, lon = float(res[0]["lat"]), float(res[0]["lon"])
    except Exception:
        return []

    query = f"""
    [out:json][timeout:50];
    (
      node["craft"="{niche_type}"](around:6000,{lat},{lon});
      way["craft"="{niche_type}"](around:6000,{lat},{lon});
      node["shop"="{niche_type}"](around:6000,{lat},{lon});
      way["shop"="{niche_type}"](around:6000,{lat},{lon});
      node["office"="{niche_type}"](around:6000,{lat},{lon});
      way["office"="{niche_type}"](around:6000,{lat},{lon});
      node["amenity"="{niche_type}"](around:6000,{lat},{lon});
      way["amenity"="{niche_type}"](around:6000,{lat},{lon});
    );
    out tags;
    """
    
    for url in overpass_urls:
        try:
            response = requests.get(url, params={'data': query}, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.json().get('elements', [])
        except Exception:
            continue
            
    return []

def check_has_website(business_name, city):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{business_name} {city}", max_results=3))
            for r in results:
                href = r.get('href', '').lower()
                if any(x in href for x in ['facebook.com', 'instagram.com', 'goudengids.be', 'opensearch', 'goldenpages']):
                    continue
                if business_name.lower().split()[0] in href:
                    return True
    except Exception:
        pass
    return False

def save_lead(naam, stad, niche, telefoon, adres, maps_url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO leads (naam, stad, niche, telefoon, adres, maps_url, sterren, aantal_reviews, eigen_score, gebeld, call_result, notes)
            VALUES (?, ?, ?, ?, ?, ?, 0.0, 0, 50, 0, '-', '')
        ''', (naam, stad, niche, telefoon, adres, maps_url))
        conn.commit()
        logging.info(f"==> LEAD FOUND: {naam} in {stad}")
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def run_worker():
    init_db()
    logging.info("Worker opgestart voor het verzamelen van leads.")
    
    while True:
        cities = load_json(CITIES_PATH, DEFAULT_CITIES)
        niches = load_json(NICHES_PATH, DEFAULT_NICHES)

        for city in cities:
            for niche in niches:
                logging.info(f"Scanning: {niche} in {city}")
                elements = get_osm_data(city, niche)
                
                for el in elements:
                    tags = el.get('tags', {})
                    naam = tags.get('name')
                    if not naam:
                        continue
                        
                    if 'website' in tags or 'contact:website' in tags:
                        continue
                        
                    telefoon = tags.get('phone') or tags.get('contact:phone') or 'Geen telefoon'
                    street = tags.get('addr:street', '')
                    housenumber = tags.get('addr:housenumber', '')
                    adres = f"{street} {housenumber}".strip() or city
                    
                    maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(naam + ' ' + city)}"

                    if not check_has_website(naam, city):
                        save_lead(naam, stad=city, niche=niche, telefoon=telefoon, adres=adres, maps_url=maps_url)
                    
                    time.sleep(1)
                time.sleep(2)
        
        logging.info("Scan-ronde afgerond. 1 uur pauze...")
        time.sleep(3600)

if __name__ == "__main__":
    run_worker()
