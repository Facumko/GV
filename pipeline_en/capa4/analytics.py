"""
pipeline_en/capa4/analytics.py
FIX CRÍTICO: DB_PATH apuntaba a viral_es.db en vez de viral_en.db.
MEJORA: Usa config.py y logger.py centralizados.
"""
import sqlite3
import json
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.config import PATHS
from shared.logger import get_logger

log     = get_logger('capa4.en.analytics')
DB_PATH = PATHS['en']['db']   # FIX: era viral_es.db


def init_performance_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY,
        video_id TEXT,
        pipeline TEXT DEFAULT 'en',
        nicho TEXT,
        hook_tipo TEXT,
        duracion_seg INTEGER,
        views_24h INTEGER DEFAULT 0,
        views_48h INTEGER DEFAULT 0,
        views_7d INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comentarios INTEGER DEFAULT 0,
        plataforma TEXT,
        fecha_publicacion DATE,
        notas TEXT
    )''')
    conn.commit()
    conn.close()


def registrar_video(video_id, nicho, hook_tipo, duracion_seg,
                    plataforma='tiktok', notas=''):
    init_performance_table()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        '''INSERT INTO performance
           (video_id, pipeline, nicho, hook_tipo, duracion_seg, plataforma, fecha_publicacion, notas)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (video_id, 'en', nicho, hook_tipo, duracion_seg,
         plataforma, datetime.now().date(), notas)
    )
    conn.commit()
    conn.close()
    log.info(f"Video EN registrado: {video_id}")


def actualizar_views(video_id, views_24h=None, views_48h=None,
                     views_7d=None, likes=None, comentarios=None):
    conn  = sqlite3.connect(DB_PATH)
    campos, valores = [], []
    for campo, val in [('views_24h', views_24h), ('views_48h', views_48h),
                       ('views_7d', views_7d), ('likes', likes),
                       ('comentarios', comentarios)]:
        if val is not None:
            campos.append(f'{campo} = ?')
            valores.append(val)
    if campos:
        valores.append(video_id)
        conn.execute(
            f'UPDATE performance SET {", ".join(campos)} WHERE video_id = ?',
            valores
        )
        conn.commit()
    conn.close()
    log.info(f"Métricas EN actualizadas para {video_id}")


def analizar_performance():
    init_performance_table()
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(
        "SELECT * FROM performance WHERE pipeline='en' AND views_24h > 0", conn
    )
    conn.close()

    if df.empty:
        log.warning("Sin datos EN. Publicá videos y registrá métricas primero.")
        return

    print(f"\n📊 PERFORMANCE REPORT [EN] — {len(df)} videos\n" + "─" * 50)

    print("\n🎯 VIEWS 24h por nicho:")
    nicho_stats = df.groupby('nicho')['views_24h'].agg(['mean', 'max', 'count'])
    nicho_stats.columns = ['avg', 'max', 'videos']
    print(nicho_stats.sort_values('avg', ascending=False).to_string())

    print("\n🪝 VIEWS 24h por tipo de hook:")
    hook_stats = df.groupby('hook_tipo')['views_24h'].agg(['mean', 'count'])
    hook_stats.columns = ['avg', 'videos']
    print(hook_stats.sort_values('avg', ascending=False).to_string())

    df['duracion_bucket'] = pd.cut(
        df['duracion_seg'], bins=[0, 30, 45, 60, 90],
        labels=['<30s', '30-45s', '45-60s', '60-90s']
    )
    print("\n⏱️  VIEWS 24h por duración:")
    print(df.groupby('duracion_bucket', observed=True)['views_24h']
            .mean().sort_values(ascending=False).to_string())

    print("\n🏆 TOP 3 VIDEOS:")
    for _, row in df.nlargest(3, 'views_24h').iterrows():
        print(f"  {row['video_id']} | {row['nicho']} | hook={row['hook_tipo']} | {row['views_24h']:,} views 24h")

    mejor_nicho = df.groupby('nicho')['views_24h'].mean().idxmax()
    mejor_hook  = df.groupby('hook_tipo')['views_24h'].mean().idxmax()
    print(f"\n✅ RECOMENDACIÓN EN: nicho='{mejor_nicho}' + hook='{mejor_hook}'")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'analizar'
    if cmd == 'registrar':
        registrar_video(
            video_id   = input("ID del video: "),
            nicho      = input("Nicho: "),
            hook_tipo  = input("Hook (pregunta/experiencia/lista/statement): "),
            duracion_seg = int(input("Duración en segundos: ")),
            plataforma = input("Plataforma (tiktok/youtube): "),
            notas      = input("Notas (opcional): ")
        )
    elif cmd == 'actualizar':
        vid   = input("ID del video: ")
        v24   = input("Views 24h (enter para saltar): ")
        v7    = input("Views 7d (enter para saltar): ")
        actualizar_views(vid,
                         views_24h=int(v24) if v24 else None,
                         views_7d=int(v7)  if v7  else None)
    else:
        analizar_performance()