import os
from dotenv import load_dotenv
from pytrends.request import TrendReq
from googleapiclient.discovery import build
import pandas as pd

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY = os.getenv('YOUTUBE_API_KEY')

NICHOS_CANDIDATOS = [
    "productivity hacks", "morning routine", "money tips", "ai tools",
    "fitness motivation", "crypto explained", "life hacks", "study with me"
]

def get_trends_score(keywords):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords[:5], timeframe='now 7-d')
    df = pytrends.interest_over_time()
    if df.empty:
        return {k: 0 for k in keywords[:5]}
    return df[keywords[:5]].mean().to_dict()

def get_youtube_views(keyword, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    req = youtube.search().list(q=keyword, part='snippet', type='video',
                                 order='viewCount', publishedAfter='2025-01-01T00:00:00Z',
                                 maxResults=5)
    res = req.execute()
    ids = [i['id']['videoId'] for i in res.get('items', [])]
    if not ids:
        return 0
    stats = youtube.videos().list(part='statistics', id=','.join(ids)).execute()
    views = [int(v['statistics'].get('viewCount', 0)) for v in stats.get('items', [])]
    return sum(views) / len(views) if views else 0

def detectar_nicho():
    print("🔍 Analizando tendencias...\n")
    trends = get_trends_score(NICHOS_CANDIDATOS[:5])
    
    resultados = []
    for nicho in NICHOS_CANDIDATOS[:5]:
        trend_score = trends.get(nicho, 0)
        yt_views = get_youtube_views(nicho, API_KEY)
        score_final = (trend_score * 0.4) + (yt_views / 1_000_000 * 0.6)
        resultados.append({'nicho': nicho, 'trend': round(trend_score, 1), 
                           'yt_views_avg': int(yt_views), 'score': round(score_final, 2)})
        print(f"  {nicho}: trend={trend_score:.0f} | yt_views={int(yt_views):,} | score={score_final:.2f}")

    df = pd.DataFrame(resultados).sort_values('score', ascending=False)
    ganador = df.iloc[0]
    print(f"\n✅ NICHO SUGERIDO: {ganador['nicho'].upper()} (score: {ganador['score']})")
    return ganador['nicho']

if __name__ == '__main__':
    detectar_nicho()