"""
Capa 4 — Analytics & Feedback Loop
Registrá performance real de tus videos y el sistema aprende qué funciona.
"""
import sqlite3
import json
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')

def init_performance_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY,
        video_id TEXT,
        pipeline TEXT DEFAULT 'es',
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

def registrar_video(video_id, nicho, hook_tipo, duracion_seg, plataforma='tiktok', notas=''):
    """Llamá esto justo después de publicar un video."""
    init_performance_table()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO performance 
        (video_id, pipeline, nicho, hook_tipo, duracion_seg, plataforma, fecha_publicacion, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (video_id, 'es', nicho, hook_tipo, duracion_seg, plataforma, datetime.now().date(), notas))
    conn.commit()
    conn.close()
    print(f"✅ Video {video_id} registrado.")

def actualizar_views(video_id, views_24h=None, views_48h=None, views_7d=None, likes=None, comentarios=None):
    """Actualizá las métricas manualmente a las 24h, 48h y 7 días."""
    conn = sqlite3.connect(DB_PATH)
    campos = []
    valores = []
    if views_24h is not None:
        campos.append('views_24h = ?'); valores.append(views_24h)
    if views_48h is not None:
        campos.append('views_48h = ?'); valores.append(views_48h)
    if views_7d is not None:
        campos.append('views_7d = ?'); valores.append(views_7d)
    if likes is not None:
        campos.append('likes = ?'); valores.append(likes)
    if comentarios is not None:
        campos.append('comentarios = ?'); valores.append(comentarios)

    if campos:
        valores.append(video_id)
        conn.execute(f'UPDATE performance SET {", ".join(campos)} WHERE video_id = ?', valores)
        conn.commit()
    conn.close()
    print(f"✅ Métricas actualizadas para {video_id}")

def analizar_performance():
    """Mostrá qué nichos, hooks y duraciones generan más views."""
    init_performance_table()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM performance WHERE pipeline='es' AND views_24h > 0", conn)
    conn.close()

    if df.empty:
        print("⚠️  Todavía no hay datos. Publicá videos y registrá sus métricas.")
        return

    print(f"\n📊 PERFORMANCE REPORT [ES] — {len(df)} videos con datos\n")
    print("─" * 50)

    # Por nicho
    print("\n🎯 VIEWS 24h por nicho:")
    nicho_stats = df.groupby('nicho')['views_24h'].agg(['mean', 'max', 'count'])
    nicho_stats.columns = ['promedio', 'máximo', 'videos']
    print(nicho_stats.sort_values('promedio', ascending=False).to_string())

    # Por hook
    print("\n🪝 VIEWS 24h por tipo de hook:")
    hook_stats = df.groupby('hook_tipo')['views_24h'].agg(['mean', 'count'])
    hook_stats.columns = ['promedio', 'videos']
    print(hook_stats.sort_values('promedio', ascending=False).to_string())

    # Duración óptima
    df['duracion_bucket'] = pd.cut(df['duracion_seg'], bins=[0, 30, 45, 60, 90], labels=['<30s', '30-45s', '45-60s', '60-90s'])
    print("\n⏱️  VIEWS 24h por duración:")
    print(df.groupby('duracion_bucket', observed=True)['views_24h'].mean().sort_values(ascending=False).to_string())

    # Top 3 videos
    print("\n🏆 TOP 3 VIDEOS:")
    for _, row in df.nlargest(3, 'views_24h').iterrows():
        print(f"  {row['video_id']} | {row['nicho']} | hook={row['hook_tipo']} | {row['views_24h']:,} views 24h")

    print("\n─" * 50)
    mejor_nicho = df.groupby('nicho')['views_24h'].mean().idxmax()
    mejor_hook = df.groupby('hook_tipo')['views_24h'].mean().idxmax()
    print(f"\n✅ RECOMENDACIÓN: Seguí con nicho '{mejor_nicho}' usando hook '{mejor_hook}'")

if __name__ == '__main__':
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'analizar'

    if cmd == 'registrar':
        # Ejemplo: python analytics.py registrar
        registrar_video(
            video_id=input("ID del video: "),
            nicho=input("Nicho: "),
            hook_tipo=input("Hook (pregunta/experiencia/lista/statement): "),
            duracion_seg=int(input("Duración en segundos: ")),
            plataforma=input("Plataforma (tiktok/youtube): "),
            notas=input("Notas (opcional): ")
        )
    elif cmd == 'actualizar':
        video_id = input("ID del video: ")
        views_24h = input("Views 24h (enter para saltar): ")
        views_7d = input("Views 7d (enter para saltar): ")
        actualizar_views(
            video_id,
            views_24h=int(views_24h) if views_24h else None,
            views_7d=int(views_7d) if views_7d else None
        )
    else:
        analizar_performance()