"""
config.py — Configuración centralizada de Granja Viral
Todos los paths, parámetros y constantes del proyecto en un solo lugar.
"""
import os

# ─── Raíz del proyecto ───────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# ─── Paths por pipeline ──────────────────────────────────────────────────────
def get_paths(pipeline: str) -> dict:
    """Retorna todos los paths relevantes para un pipeline ('es' o 'en')."""
    base = os.path.join(ROOT, f'pipeline_{pipeline}')
    data = os.path.join(base, 'data')
    return {
        'base':           base,
        'data':           data,
        'db':             os.path.join(data, f'viral_{pipeline}.db'),
        'audio':          os.path.join(data, 'audio_001.mp3'),
        'timestamps':     os.path.join(data, 'timestamps_001.json'),
        'capa1':          os.path.join(base, 'capa1'),
        'capa2':          os.path.join(base, 'capa2'),
        'capa3':          os.path.join(base, 'capa3'),
        'capa4':          os.path.join(base, 'capa4'),
        'video_out':      os.path.join(base, 'capa3', 'out', 'video_001.mp4'),
        'guiones_dir':    data,
    }

PATHS = {
    'es': get_paths('es'),
    'en': get_paths('en'),
    'shared': os.path.join(ROOT, 'shared'),
    'logs':   os.path.join(ROOT, 'logs'),
    'env':    os.path.join(ROOT, '.env'),
}

# ─── Modelos de IA ───────────────────────────────────────────────────────────
OLLAMA = {
    'url':   'http://localhost:11434/api/generate',
    'model': 'llama3:8b',
    'timeout': 120,
}

# ─── TTS ─────────────────────────────────────────────────────────────────────
TTS_VOICES = {
    'es': 'es-AR-TomasNeural',   # Alternativa: es-MX-JorgeNeural
    'en': 'en-US-GuyNeural',     # Alternativa: en-US-JennyNeural
}

# ─── Whisper ─────────────────────────────────────────────────────────────────
WHISPER = {
    'model':    'small',
    'language': {'es': 'es', 'en': 'en'},
}

# ─── Video ───────────────────────────────────────────────────────────────────
VIDEO = {
    'fps':    30,
    'width':  1080,
    'height': 1920,
    'duration_frames': 360,   # 12 segundos a 30fps — ajustá según audio real
}

# ─── Scraper ─────────────────────────────────────────────────────────────────
SCRAPER = {
    'max_results':      10,
    'published_after':  '2025-01-01T00:00:00Z',
    'viral_threshold':  50_000,   # views mínimas para considerar viral
}

# ─── Nichos por defecto ──────────────────────────────────────────────────────
DEFAULT_NICHOS = {
    'es': 'rutina mañana',
    'en': 'morning routine',
}

# ─── Hook keywords ───────────────────────────────────────────────────────────
HOOK_KEYWORDS = {
    'pregunta': {
        'es': ['cómo', 'por qué', 'qué', 'cuándo', 'cuál'],
        'en': ['how', 'why', 'what', 'when', 'which'],
    },
    'experiencia': {
        'es': ['probé', 'hice', 'intenté', 'pasé', 'viví'],
        'en': ['i tried', 'i did', 'i spent', 'i tested', 'i quit'],
    },
}