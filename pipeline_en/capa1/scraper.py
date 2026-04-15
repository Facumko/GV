import os
import sqlite3
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
API_KEY = os.getenv('YOUTUBE_API_KEY')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')

def init_db():
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

def duracion_a_segundos(iso):
    import re
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not match:
        return 0
    h, m, s = [int(x or 0) for x in match.groups()]
    return h*3600 + m*60 + s

def scrape_nicho(nicho, max_results=10):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    res = youtube.search().list(q=nicho, part='snippet', type='video',
                                 order='viewCount', publishedAfter='2025-01-01T00:00:00Z',
                                 maxResults=max_results).execute()
    ids = [i['id']['videoId'] for i in res.get('items', [])]
    snippets = {i['id']['videoId']: i['snippet'] for i in res.get('items', [])}

    stats_res = youtube.videos().list(part='statistics,contentDetails', id=','.join(ids)).execute()

    conn = init_db()
    guardados = 0
    for v in stats_res.get('items', []):
        vid_id = v['id']
        stats = v['statistics']
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        duracion = duracion_a_segundos(v['contentDetails']['duration'])
        engagement = (likes + comments) / views if views else 0
        titulo = snippets.get(vid_id, {}).get('title', '')
        
        # Hook tipo simple basado en título
        if any(w in titulo.lower() for w in ['how', 'why', 'what', 'cómo', 'por qué']):
            hook = 'pregunta'
        elif any(w in titulo.lower() for w in ['i tried', 'i did', 'probé', 'hice']):
            hook = 'experiencia'
        elif titulo[0].isdigit():
            hook = 'lista'
        else:
            hook = 'statement'

        estructura = json.dumps({'titulo': titulo, 'views': views, 'likes': likes})
        url = f'https://youtube.com/watch?v={vid_id}'

        conn.execute('''INSERT INTO patrones_virales 
            (fuente_url, nicho, duracion_seg, hook_tipo, ratio_engagement, estructura, fecha_analisis)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (url, nicho, duracion, hook, round(engagement, 4), estructura, datetime.now().date()))
        guardados += 1

    conn.commit()
    conn.close()
    print(f"✅ {guardados} videos guardados para nicho: {nicho}")

if __name__ == '__main__':
    scrape_nicho('morning routine')