import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS videos_generados (
        id INTEGER PRIMARY KEY,
        guion_hook TEXT,
        audio_path TEXT,
        video_path TEXT,
        pipeline TEXT,
        publicado BOOLEAN DEFAULT 0,
        fecha DATE
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY,
        video_id INTEGER,
        plataforma TEXT,
        pipeline TEXT,
        views_24h INTEGER DEFAULT 0,
        views_48h INTEGER DEFAULT 0,
        views_7d INTEGER DEFAULT 0,
        viral BOOLEAN DEFAULT 0
    )''')
    conn.commit()
    return conn

def registrar_video(hook, audio, video):
    conn = init_db()
    conn.execute('''INSERT INTO videos_generados (guion_hook, audio_path, video_path, pipeline, fecha)
        VALUES (?, ?, ?, ?, ?)''', (hook, audio, video, 'es', datetime.now().date()))
    conn.commit()
    vid_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    print(f"✅ Video registrado con ID: {vid_id}")
    return vid_id

def registrar_performance(video_id, plataforma, views_24h, views_48h, views_7d):
    conn = init_db()
    viral = views_7d > 50000
    conn.execute('''INSERT INTO performance (video_id, plataforma, pipeline, views_24h, views_48h, views_7d, viral)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (video_id, plataforma, 'es', views_24h, views_48h, views_7d, viral))
    conn.commit()
    conn.close()
    print(f"✅ Performance guardada — viral: {viral}")

if __name__ == '__main__':
    vid_id = registrar_video(
        hook="La mañana es el reto de todos",
        audio="../data/audio_001.mp3",
        video="../capa3/out/video_001.mp4"
    )
    print(f"Probá registrar performance con: registrar_performance({vid_id}, 'tiktok', 0, 0, 0)")