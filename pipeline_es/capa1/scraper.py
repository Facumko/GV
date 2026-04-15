"""
pipeline_es/capa1/scraper.py
FIX: IndexError en titulo[0] cuando título está vacío.
MEJORA: Usa config.py y logger.py centralizados.
"""
import os
import sys
import sqlite3
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.config import PATHS, SCRAPER, HOOK_KEYWORDS
from shared.logger import get_logger

log = get_logger('capa1.es.scraper')

load_dotenv(dotenv_path=PATHS['env'])
API_KEY = os.getenv('YOUTUBE_API_KEY')
DB_PATH = PATHS['es']['db']


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS patrones_virales (
        id INTEGER PRIMARY KEY,
        fuente_url TEXT,
        nicho TEXT,
        duracion_seg INTEGER,
        hook_tipo TEXT,
        ratio_engagement REAL,
        estructura JSON,
        fecha_analisis DATE
    )''')
    conn.commit()
    return conn


def duracion_a_segundos(iso: str) -> int:
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not match:
        return 0
    h, m, s = [int(x or 0) for x in match.groups()]
    return h * 3600 + m * 60 + s


def clasificar_hook(titulo: str, pipeline: str = 'es') -> str:
    t = titulo.lower()
    for keyword in HOOK_KEYWORDS['pregunta'][pipeline]:
        if keyword in t:
            return 'pregunta'
    for keyword in HOOK_KEYWORDS['experiencia'][pipeline]:
        if keyword in t:
            return 'experiencia'
    if titulo and titulo[0].isdigit():   # FIX: guarda contra título vacío
        return 'lista'
    return 'statement'


def scrape_nicho(nicho: str, max_results: int = SCRAPER['max_results']) -> int:
    if not API_KEY:
        log.error("YOUTUBE_API_KEY no encontrada en .env")
        return 0

    log.info(f"Scrapeando nicho [ES]: '{nicho}' ({max_results} videos)")

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    res = youtube.search().list(
        q=nicho, part='snippet', type='video',
        order='viewCount',
        publishedAfter=SCRAPER['published_after'],
        maxResults=max_results
    ).execute()

    ids = [i['id']['videoId'] for i in res.get('items', [])]
    snippets = {i['id']['videoId']: i['snippet'] for i in res.get('items', [])}

    if not ids:
        log.warning(f"No se encontraron videos para: {nicho}")
        return 0

    stats_res = youtube.videos().list(
        part='statistics,contentDetails', id=','.join(ids)
    ).execute()

    conn = init_db()
    guardados = 0
    for v in stats_res.get('items', []):
        vid_id  = v['id']
        stats   = v['statistics']
        views   = int(stats.get('viewCount', 0))
        likes   = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        duracion = duracion_a_segundos(v['contentDetails']['duration'])
        engagement = (likes + comments) / views if views else 0
        titulo = snippets.get(vid_id, {}).get('title', '')
        hook   = clasificar_hook(titulo, 'es')

        estructura = json.dumps({'titulo': titulo, 'views': views, 'likes': likes})
        url = f'https://youtube.com/watch?v={vid_id}'

        conn.execute(
            '''INSERT INTO patrones_virales
               (fuente_url, nicho, duracion_seg, hook_tipo, ratio_engagement, estructura, fecha_analisis)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (url, nicho, duracion, hook, round(engagement, 4), estructura, datetime.now().date())
        )
        guardados += 1

    conn.commit()
    conn.close()
    log.info(f"{guardados} videos guardados para nicho ES: '{nicho}'")
    return guardados


if __name__ == '__main__':
    nicho = sys.argv[1] if len(sys.argv) > 1 else 'rutina mañana'
    scrape_nicho(nicho)