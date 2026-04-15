import os
from dotenv import load_dotenv
from pytrends.request import TrendReq
from googleapiclient.discovery import build
import pandas as pd

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
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

def get_trends_score(keywords, lang='en'):
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
        print(f"  ⚠️  Trends error: {e}")
        return {k: 0 for k in keywords[:5]}

def get_youtube_views(keyword):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        res = youtube.search().list(
            q=keyword, part='snippet', type='video',
            order='viewCount', publishedAfter='2025-01-01T00:00:00Z',
            maxResults=5
        ).execute()
        ids = [i['id']['videoId'] for i in res.get('items', [])]
        if not ids:
            return 0
        stats = youtube.videos().list(part='statistics', id=','.join(ids)).execute()
        views = [int(v['statistics'].get('viewCount', 0)) for v in stats.get('items', [])]
        return sum(views) / len(views) if views else 0
    except Exception as e:
        print(f"  ⚠️  YouTube error: {e}")
        return 0

def detectar_nicho(pipeline='es'):
    """
    pipeline: 'es' o 'en'
    Retorna el nicho ganador como string.
    """
    nichos = NICHOS[pipeline]
    print(f"\n🔍 Analizando tendencias [{pipeline.upper()}]...\n")

    trends = get_trends_score(nichos[:5], lang=pipeline)

    resultados = []
    for nicho in nichos[:5]:
        trend_score = trends.get(nicho, 0)
        yt_views = get_youtube_views(nicho)
        score_final = (trend_score * 0.4) + (yt_views / 1_000_000 * 0.6)
        resultados.append({
            'nicho': nicho,
            'trend': round(trend_score, 1),
            'yt_views_avg': int(yt_views),
            'score': round(score_final, 2)
        })
        print(f"  {nicho}: trend={trend_score:.0f} | yt_views={int(yt_views):,} | score={score_final:.2f}")

    df = pd.DataFrame(resultados).sort_values('score', ascending=False)
    ganador = df.iloc[0]

    print(f"\n✅ NICHO SUGERIDO [{pipeline.upper()}]: {ganador['nicho'].upper()} (score: {ganador['score']})")
    confirmar = input("\n¿Aceptás este nicho? (s/n): ").strip().lower()
    if confirmar != 's':
        print("Nichos disponibles:")
        for i, row in df.iterrows():
            print(f"  {i+1}. {row['nicho']} (score: {row['score']})")
        idx = int(input("Elegí número: ")) - 1
        return df.iloc[idx]['nicho']

    return ganador['nicho']

if __name__ == '__main__':
    import sys
    pipeline = sys.argv[1] if len(sys.argv) > 1 else 'es'
    detectar_nicho(pipeline)