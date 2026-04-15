import os
import requests
import sqlite3
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_patron():
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        'SELECT nicho, hook_tipo, duracion_seg FROM patrones_virales ORDER BY ratio_engagement DESC LIMIT 1'
    ).fetchone()
    conn.close()
    return {'nicho': row[0], 'hook': row[1], 'duracion': row[2]}

def generar_guion(patron):
    prompt = f"""Generá 3 guiones cortos para un video viral de {patron['duracion']}s sobre "{patron['nicho']}".
Cada guion debe tener:
- HOOK (primeros 3 segundos, estilo {patron['hook']} — enganchá de inmediato)
- CONFLICTO (problema, tensión o dato sorprendente)
- RESOLUCION (payoff inesperado o satisfactorio)

Usá español latino, tono casual y directo. Máximo 80 palabras por guion.

Formato exacto:
GUION 1:
HOOK: ...
CONFLICTO: ...
RESOLUCION: ...

GUION 2:
HOOK: ...
CONFLICTO: ...
RESOLUCION: ...

GUION 3:
HOOK: ...
CONFLICTO: ...
RESOLUCION: ..."""

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
    print("✍️  Generando guiones...\n")
    guiones = generar_guion(patron)
    print(guiones)
    guardar_guion(guiones, patron)