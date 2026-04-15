"""
shared/niche_detector.py
FIX: índice roto al mostrar lista de nichos alternativos (usaba df.iterrows() index).
MEJORA: Usa config.py y logger.py centralizados.
"""
import os
import sys
from dotenv import load_dotenv
from pytrends.request import TrendReq
from googleapiclient.discovery import build
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from shared.config import PATHS, SCRAPER
from shared.logger import get_logger

log = get_logger('shared.niche_detector')

load_dotenv(dotenv_path=PATHS['env'])
API_KEY = os.getenv('YOUTUBE_API_KEY')

NICHOS = {
    'en': [
        "productivity hacks", "morning routine", "money tips",
        "ai tools 2025", "fitness motivation", "life hacks",
        "study with me", "passive income"
    ],
    'es': [
        "rutina mañana", "consejos dinero", "herramientas ia",
        "motivacion fitness", "habitos exitosos", "trucos vida",
        "emprender desde cero", "finanzas personales"
    ]
}


def get_trends_score(keywords: list, lang: str = 'en') -> dict:
    hl = 'en-US' if lang == 'en' else 'es-419'
    try:
        pytrends = TrendReq(hl=hl, tz=360)
        pytrends.build_payload(keywords[:5], timeframe='now 7-d')
        df = pytrends.interest_over_time()
        if df.empty:
            return {k: 0 for k in keywords[:5]}
        cols = [c for c in keywords[:5] if c in df.columns]
        return df[cols].mean().to_dict()
    except Exception as e:
        log.warning(f"Trends error: {e}")
        return {k: 0 for k in keywords[:5]}


def get_youtube_views(keyword: str) -> float:
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        res = youtube.search().list(
            q=keyword, part='snippet', type='video',
            order='viewCount',
            publishedAfter=SCRAPER['published_after'],
            maxResults=5
        ).execute()
        ids = [i['id']['videoId'] for i in res.get('items', [])]
        if not ids:
            return 0
        stats = youtube.videos().list(part='statistics', id=','.join(ids)).execute()
        views = [int(v['statistics'].get('viewCount', 0)) for v in stats.get('items', [])]
        return sum(views) / len(views) if views else 0
    except Exception as e:
        log.warning(f"YouTube error para '{keyword}': {e}")
        return 0


def detectar_nicho(pipeline: str = 'es') -> str:
    """
    Detecta el nicho más prometedor para el pipeline dado.
    Retorna el nicho como string.
    """
    nichos = NICHOS[pipeline]
    log.info(f"Analizando tendencias [{pipeline.upper()}]...")

    trends = get_trends_score(nichos[:5], lang=pipeline)

    resultados = []
    for nicho in nichos[:5]:
        trend_score = trends.get(nicho, 0)
        yt_views    = get_youtube_views(nicho)
        score_final = (trend_score * 0.4) + (yt_views / 1_000_000 * 0.6)
        resultados.append({
            'nicho':       nicho,
            'trend':       round(trend_score, 1),
            'yt_views_avg': int(yt_views),
            'score':       round(score_final, 2)
        })
        print(f"  {nicho}: trend={trend_score:.0f} | yt_views={int(yt_views):,} | score={score_final:.2f}")

    # FIX: reset_index() para que el índice sea 0,1,2... y no el del DataFrame
    df = pd.DataFrame(resultados).sort_values('score', ascending=False).reset_index(drop=True)
    ganador = df.iloc[0]

    log.info(f"Nicho sugerido [{pipeline.upper()}]: {ganador['nicho'].upper()} (score: {ganador['score']})")
    confirmar = input("\n¿Aceptás este nicho? (s/n): ").strip().lower()

    if confirmar == 's':
        return ganador['nicho']

    # FIX: ahora i es 0,1,2... gracias al reset_index
    print("\nNichos disponibles:")
    for i, row in df.iterrows():
        print(f"  {i + 1}. {row['nicho']} (score: {row['score']})")

    while True:
        try:
            idx = int(input("Elegí número: ")) - 1
            if 0 <= idx < len(df):
                return df.iloc[idx]['nicho']
            print(f"Número inválido. Ingresá entre 1 y {len(df)}.")
        except ValueError:
            print("Ingresá un número válido.")


if __name__ == '__main__':
    pipeline = sys.argv[1] if len(sys.argv) > 1 else 'es'
    resultado = detectar_nicho(pipeline)
    print(f"\n✅ Nicho elegido: {resultado}")