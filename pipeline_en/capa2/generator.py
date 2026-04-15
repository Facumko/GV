import os
import requests
import sqlite3
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')

def get_patron():
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute('SELECT nicho, hook_tipo, duracion_seg FROM patrones_virales ORDER BY ratio_engagement DESC LIMIT 1').fetchone()
    conn.close()
    return {'nicho': row[0], 'hook': row[1], 'duracion': row[2]}

def generar_guion(patron):
    prompt = f"""Generá 3 guiones cortos para un video viral de {patron['duracion']}s sobre "{patron['nicho']}".
Cada guion debe tener:
- HOOK (primeros 3 segundos, estilo {patron['hook']})
- CONFLICTO (problema o tension)
- RESOLUCION (inesperada o sorprendente)

Respondé en español latino. Formato:
GUION 1:
HOOK: ...
CONFLICTO: ...
RESOLUCION: ...

GUION 2:
...

GUION 3:
..."""

    res = requests.post('http://localhost:11434/api/generate',
                        json={'model': 'llama3:8b', 'prompt': prompt, 'stream': False})
    return res.json()['response']

if __name__ == '__main__':
    patron = get_patron()
    print(f"📌 Patrón base: {patron}\n")
    print("✍️ Generando guiones...\n")
    guiones = generar_guion(patron)
    print(guiones)