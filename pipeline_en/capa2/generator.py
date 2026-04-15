import os
import requests
import sqlite3
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_en.db')  # FIX: era viral_es
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_patron():
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        'SELECT nicho, hook_tipo, duracion_seg FROM patrones_virales ORDER BY ratio_engagement DESC LIMIT 1'
    ).fetchone()
    conn.close()
    return {'nicho': row[0], 'hook': row[1], 'duracion': row[2]}

def generar_guion(patron):
    prompt = f"""Generate 3 short scripts for a {patron['duracion']}-second viral short video about "{patron['nicho']}".
Each script must have:
- HOOK (first 3 seconds, style: {patron['hook']} — grab attention immediately)
- CONFLICT (a problem, tension, or surprising fact)
- RESOLUTION (unexpected or satisfying payoff)

Keep language casual, punchy, American English. Each script max 80 words.

Format exactly like this:
SCRIPT 1:
HOOK: ...
CONFLICT: ...
RESOLUTION: ...

SCRIPT 2:
HOOK: ...
CONFLICT: ...
RESOLUTION: ...

SCRIPT 3:
HOOK: ...
CONFLICT: ...
RESOLUTION: ..."""

    res = requests.post(
        'http://localhost:11434/api/generate',
        json={'model': 'llama3:8b', 'prompt': prompt, 'stream': False},
        timeout=120
    )
    return res.json()['response']

def guardar_guion(texto, patron):
    os.makedirs(DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(DATA_DIR, f'guion_{timestamp}.json')
    data = {'nicho': patron['nicho'], 'hook': patron['hook'], 'guiones_raw': texto, 'fecha': timestamp}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Guion guardado en: {path}")
    return path

if __name__ == '__main__':
    patron = get_patron()
    print(f"📌 Patrón base: {patron}\n")
    print("✍️  Generando guiones en inglés...\n")
    guiones = generar_guion(patron)
    print(guiones)
    guardar_guion(guiones, patron)