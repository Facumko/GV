import sqlite3
import json
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'viral_es.db')

def analizar():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM patrones_virales ORDER BY ratio_engagement DESC', conn)
    conn.close()

    print(f"\n📊 ANÁLISIS — {len(df)} videos\n")
    print(f"Hook más común: {df['hook_tipo'].value_counts().idxmax()}")
    print(f"Duración promedio: {df['duracion_seg'].mean():.0f}s")
    print(f"Engagement promedio: {df['ratio_engagement'].mean():.4f}")
    print(f"\nTop 3 videos:\n")

    for _, row in df.head(3).iterrows():
        datos = json.loads(row['estructura'])
        print(f"  🎬 {datos['titulo'][:60]}")
        print(f"     hook={row['hook_tipo']} | dur={row['duracion_seg']}s | eng={row['ratio_engagement']:.4f}\n")

if __name__ == '__main__':
    analizar()