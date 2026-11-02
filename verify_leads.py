import sqlite3
import socket

DB_PATH = "/home/jelle/leadfinder/leads.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure verification_status column exists
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN verification_status TEXT DEFAULT 'Unverified'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def check_domain_exists(company_name, city):
    clean_name = company_name.lower().replace(" ", "").replace("-", "").replace(".", "").replace("&", "")
    domains = [f"www.{clean_name}.be", f"www.{clean_name}.nl", f"www.{clean_name}-{city.lower()}.be"]
    
    for domain in domains:
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            continue
    return False

def verify_all_leads():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, naam, stad FROM leads WHERE is_deleted = 0 OR is_deleted IS NULL")
    leads = cursor.fetchall()

    print(f"🔍 Verifying {len(leads)} leads for active web domains...\n")

    no_website_count = 0
    potential_website_count = 0

    for lead in leads:
        lead_id, name, city = lead
        has_domain = check_domain_exists(name, city)
        
        status = "Potential Website" if has_domain else "No Website"
        if has_domain:
            potential_website_count += 1
        else:
            no_website_count += 1

        cursor.execute("UPDATE leads SET verification_status = ? WHERE id = ?", (status, lead_id))

    conn.commit()
    conn.close()

    print("="*60)
    print("VERIFICATION COMPLETED")
    print("="*60)
    print(f"✅ Verified No Website: {no_website_count}")
    print(f"⚠️ Potential Website / Ambiguous: {potential_website_count}")
    print("="*60)

if __name__ == "__main__":
    verify_all_leads()
