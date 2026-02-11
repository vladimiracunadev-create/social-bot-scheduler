#!/usr/bin/env python3
"""
Script compartido para verificar idempotencia usando SQLite.
Usado por todos los workflows de n8n (casos 01-08).
"""
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuración
SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR / "shared" / "fingerprints.db"
TTL_HOURS = 24

def init_db():
    """Inicializa la base de datos SQLite si no existe."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            fingerprint TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            processed_at TEXT NOT NULL,
            payload TEXT
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_processed_at 
        ON fingerprints(processed_at)
    """)
    
    conn.commit()
    conn.close()

def cleanup_expired():
    """Elimina fingerprints expirados (> TTL_HOURS)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff = (datetime.now() - timedelta(hours=TTL_HOURS)).isoformat()
    
    cursor.execute("""
        DELETE FROM fingerprints 
        WHERE processed_at < ?
    """, (cutoff,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

def check_fingerprint(fingerprint, case_id):
    """Verifica si un fingerprint ya fue procesado."""
    init_db()
    cleanup_expired()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 1 FROM fingerprints 
        WHERE fingerprint = ? AND case_id = ?
    """, (fingerprint, case_id))
    
    exists = cursor.fetchone() is not None
    conn.close()
    
    return exists

def add_fingerprint(fingerprint, case_id, payload=None):
    """Agrega un nuevo fingerprint al registro."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO fingerprints (fingerprint, case_id, processed_at, payload)
            VALUES (?, ?, ?, ?)
        """, (fingerprint, case_id, datetime.now().isoformat(), payload))
        
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Fingerprint ya existe (race condition)
        success = False
    finally:
        conn.close()
    
    return success

def get_stats(case_id=None):
    """Obtiene estadísticas de fingerprints."""
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if case_id:
        cursor.execute("""
            SELECT COUNT(*) FROM fingerprints WHERE case_id = ?
        """, (case_id,))
    else:
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
    
    total = cursor.fetchone()[0]
    conn.close()
    
    return {"total": total, "case_id": case_id}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: check_idempotency.py <action> [args]"}))
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check" and len(sys.argv) == 4:
        fingerprint = sys.argv[2]
        case_id = sys.argv[3]
        exists = check_fingerprint(fingerprint, case_id)
        print(json.dumps({"exists": exists, "fingerprint": fingerprint, "case": case_id}))
    
    elif action == "add" and len(sys.argv) >= 4:
        fingerprint = sys.argv[2]
        case_id = sys.argv[3]
        payload = sys.argv[4] if len(sys.argv) > 4 else None
        success = add_fingerprint(fingerprint, case_id, payload)
        print(json.dumps({"added": success, "fingerprint": fingerprint, "case": case_id}))
    
    elif action == "stats":
        case_id = sys.argv[2] if len(sys.argv) > 2 else None
        stats = get_stats(case_id)
        print(json.dumps(stats))
    
    elif action == "cleanup":
        deleted = cleanup_expired()
        print(json.dumps({"cleaned": deleted}))
    
    else:
        print(json.dumps({"error": f"Invalid action '{action}'. Use: check, add, stats, cleanup"}))
        sys.exit(1)
