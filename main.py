#!/usr/bin/env python3
"""
main.py — Orquestador principal de Granja Viral
Ejecuta el pipeline completo o pasos individuales.

USO:
  python main.py                        # pipeline ES completo
  python main.py --pipeline en          # pipeline EN completo
  python main.py --pipeline both        # ambos pipelines
  python main.py --pipeline es --steps scrape generate tts timestamps
  python main.py --pipeline es --skip-render
  python main.py --pipeline es --nicho "rutina mañana"
  python main.py --detect-niche         # solo detección de nicho
  python main.py --analytics            # reporte de performance

PASOS DISPONIBLES:
  detect    → detectar nicho con pytrends + YouTube
  scrape    → scrapear videos del nicho en YouTube
  analyze   → analizar patrones en la DB
  generate  → generar guiones con Ollama
  tts       → generar audio con Edge-TTS
  timestamps → transcribir con Whisper
  render    → renderizar video con Remotion
  register  → registrar video en DB de performance
"""
import argparse
import os
import sys
import subprocess
import shutil
import asyncio
from datetime import datetime

# ─── Path setup ──────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from shared.config import PATHS, OLLAMA, TTS_VOICES, WHISPER, DEFAULT_NICHOS
from shared.logger import get_logger

log = get_logger('main')

ALL_STEPS = ['detect', 'scrape', 'analyze', 'generate', 'tts', 'timestamps', 'render', 'register']


# ─── Helpers ─────────────────────────────────────────────────────────────────

def separator(titulo: str):
    ancho = 60
    print(f"\n{'═' * ancho}")
    print(f"  {titulo}")
    print(f"{'═' * ancho}\n")


def check_ollama():
    import requests
    try:
        r = requests.get('http://localhost:11434', timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def check_ffmpeg():
    return shutil.which('ffmpeg') is not None


def check_node():
    return shutil.which('node') is not None


def preflight_checks():
    """Verifica dependencias críticas antes de arrancar."""
    separator("🔍 PREFLIGHT CHECKS")
    ok = True

    checks = [
        ('Ollama',  check_ollama,  "Inicialo con: ollama serve"),
        ('FFmpeg',  check_ffmpeg,  "Instalalo con: sudo apt install ffmpeg"),
        ('Node.js', check_node,    "Instalalo desde: https://nodejs.org"),
    ]

    for nombre, fn, hint in checks:
        if fn():
            log.info(f"{nombre} — OK")
        else:
            log.warning(f"{nombre} — NO ENCONTRADO. {hint}")
            ok = False

    env_path = PATHS['env']
    if os.path.exists(env_path):
        log.info(".env — OK")
    else:
        log.warning(".env no encontrado. Copiá .env.example a .env y completá la API key.")
        ok = False

    return ok


# ─── Pasos del pipeline ───────────────────────────────────────────────────────

def step_detect(pipeline: str, nicho_override: str = None) -> str:
    """Detecta el nicho más prometedor. Retorna el nicho elegido."""
    if nicho_override:
        log.info(f"Nicho forzado: '{nicho_override}'")
        return nicho_override

    separator(f"🔍 PASO 1 — DETECTAR NICHO [{pipeline.upper()}]")
    try:
        from shared.niche_detector import detectar_nicho
        return detectar_nicho(pipeline)
    except ImportError as e:
        log.warning(f"niche_detector no disponible ({e}). Usando nicho por defecto.")
        return DEFAULT_NICHOS[pipeline]


def step_scrape(pipeline: str, nicho: str) -> bool:
    separator(f"📡 PASO 2 — SCRAPE [{pipeline.upper()}] nicho='{nicho}'")
    try:
        if pipeline == 'es':
            from pipeline_es.capa1.scraper import scrape_nicho
        else:
            from pipeline_en.capa1.scraper import scrape_nicho
        guardados = scrape_nicho(nicho)
        return guardados > 0
    except Exception as e:
        log.error(f"Error en scrape [{pipeline}]: {e}")
        return False


def step_analyze(pipeline: str) -> dict | None:
    separator(f"📊 PASO 3 — ANALYZE [{pipeline.upper()}]")
    try:
        if pipeline == 'es':
            from pipeline_es.capa1.analyzer import analizar
        else:
            from pipeline_en.capa1.analyzer import analizar
        return analizar()
    except Exception as e:
        log.error(f"Error en analyze [{pipeline}]: {e}")
        return None


def step_generate(pipeline: str) -> str | None:
    separator(f"✍️  PASO 4 — GENERAR GUIÓN [{pipeline.upper()}]")

    if not check_ollama():
        log.error("Ollama no está corriendo. Inicialo con: ollama serve")
        return None
    try:
        if pipeline == 'es':
            from pipeline_es.capa2.generator import get_patron, generar_guion, guardar_guion
        else:
            from pipeline_en.capa2.generator import get_patron, generar_guion, guardar_guion

        patron  = get_patron()
        log.info(f"Patrón base: {patron}")
        guiones = generar_guion(patron)
        print(f"\n{guiones}\n")
        path    = guardar_guion(guiones, patron)
        return path
    except Exception as e:
        log.error(f"Error en generate [{pipeline}]: {e}")
        return None


def step_tts(pipeline: str, texto: str = None) -> bool:
    separator(f"🎙️  PASO 5 — TTS [{pipeline.upper()}]")

    # Texto de ejemplo si no se pasa uno
    if not texto:
        if pipeline == 'es':
            texto = (
                "La mañana es el reto de todos. "
                "Pero cuando el ritmo se rompe, todo se complica. "
                "Entonces decidió tomar un enfoque más extraño. ¡Y funcionó!"
            )
        else:
            texto = (
                "You've been doing your morning wrong your whole life. "
                "Most people start with coffee — and that's exactly the problem. "
                "Try this instead for 7 days. The results will shock you."
            )

    try:
        import edge_tts
        voz        = TTS_VOICES[pipeline]
        output_dir = PATHS[pipeline]['data']
        output_path = os.path.join(output_dir, 'audio_001.mp3')
        os.makedirs(output_dir, exist_ok=True)

        async def _generar():
            communicate = edge_tts.Communicate(texto, voz)
            await communicate.save(output_path)

        asyncio.run(_generar())
        log.info(f"Audio guardado: {output_path}")

        # Remotion necesita el audio en /public/
        public_dir  = os.path.join(PATHS[pipeline]['capa3'], 'public')
        os.makedirs(public_dir, exist_ok=True)
        dest        = os.path.join(public_dir, 'audio_001.mp3')
        shutil.copy2(output_path, dest)
        log.info(f"Audio copiado a Remotion public/: {dest}")
        return True

    except ImportError:
        log.error("edge_tts no instalado. Ejecutá: pip install edge-tts")
        return False
    except Exception as e:
        log.error(f"Error en TTS [{pipeline}]: {e}")
        return False


def step_timestamps(pipeline: str) -> bool:
    separator(f"⏱️  PASO 6 — TIMESTAMPS [{pipeline.upper()}]")
    try:
        if pipeline == 'es':
            from pipeline_es.capa2.timestamps import generar_timestamps
        else:
            from pipeline_en.capa2.timestamps import generar_timestamps
        generar_timestamps()
        return True
    except ImportError:
        log.error("whisper no instalado. Ejecutá: pip install openai-whisper")
        return False
    except Exception as e:
        log.error(f"Error en timestamps [{pipeline}]: {e}")
        return False


def step_render(pipeline: str) -> bool:
    separator(f"🎬 PASO 7 — RENDER [{pipeline.upper()}]")

    if not check_node():
        log.error("Node.js no encontrado.")
        return False
    if not check_ffmpeg():
        log.error("FFmpeg no encontrado.")
        return False

    capa3_dir = PATHS[pipeline]['capa3']
    node_modules = os.path.join(capa3_dir, 'node_modules')

    if not os.path.exists(node_modules):
        log.info("node_modules no encontrado — ejecutando npm install...")
        result = subprocess.run(['npm', 'install'], cwd=capa3_dir, capture_output=True, text=True)
        if result.returncode != 0:
            log.error(f"npm install falló:\n{result.stderr}")
            return False
        log.info("npm install completado.")

    log.info(f"Renderizando video [{pipeline.upper()}]...")
    out_dir = os.path.join(capa3_dir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    result = subprocess.run(
        ['npx', 'remotion', 'render', 'src/index.js', 'VideoViral', 'out/video_001.mp4'],
        cwd=capa3_dir,
        capture_output=False,   # mostrar output en tiempo real
        text=True
    )

    if result.returncode == 0:
        log.info(f"Video renderizado: {out_dir}/video_001.mp4")
        return True
    else:
        log.error(f"Render falló con código {result.returncode}")
        return False


def step_register(pipeline: str, nicho: str, hook: str = 'statement', duracion: int = 12):
    separator(f"📝 PASO 8 — REGISTRAR VIDEO [{pipeline.upper()}]")
    try:
        if pipeline == 'es':
            from pipeline_es.capa4.registro import registrar_video
            vid_id = registrar_video(
                hook=hook,
                audio=PATHS[pipeline]['audio'],
                video=PATHS[pipeline]['video_out']
            )
        else:
            from pipeline_en.capa4.analytics import registrar_video
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            registrar_video(
                video_id=f"video_{timestamp}",
                nicho=nicho,
                hook_tipo=hook,
                duracion_seg=duracion,
            )
        log.info("Video registrado en DB.")
    except Exception as e:
        log.error(f"Error al registrar video: {e}")


def step_analytics(pipeline: str):
    separator(f"📈 ANALYTICS [{pipeline.upper()}]")
    try:
        if pipeline == 'es':
            from pipeline_es.capa4.analytics import analizar_performance
        else:
            from pipeline_en.capa4.analytics import analizar_performance
        analizar_performance()
    except Exception as e:
        log.error(f"Error en analytics [{pipeline}]: {e}")


# ─── Runner ──────────────────────────────────────────────────────────────────

def run_pipeline(pipeline: str, steps: list, nicho_override: str = None,
                 tts_texto: str = None, skip_checks: bool = False):
    """Ejecuta los pasos del pipeline en orden."""

    log.info(f"Iniciando pipeline [{pipeline.upper()}] — pasos: {steps}")
    nicho = nicho_override or DEFAULT_NICHOS[pipeline]
    resultados = {}

    for step in steps:
        if step == 'detect':
            nicho = step_detect(pipeline, nicho_override)
            resultados['nicho'] = nicho

        elif step == 'scrape':
            ok = step_scrape(pipeline, nicho)
            resultados['scrape'] = ok
            if not ok:
                log.warning("Scrape sin resultados — continuando de todos modos.")

        elif step == 'analyze':
            step_analyze(pipeline)

        elif step == 'generate':
            path = step_generate(pipeline)
            resultados['guion'] = path

        elif step == 'tts':
            ok = step_tts(pipeline, tts_texto)
            resultados['tts'] = ok
            if not ok:
                log.error("TTS falló — abortando pipeline.")
                return resultados

        elif step == 'timestamps':
            ok = step_timestamps(pipeline)
            resultados['timestamps'] = ok
            if not ok:
                log.error("Timestamps fallaron — abortando pipeline.")
                return resultados

        elif step == 'render':
            ok = step_render(pipeline)
            resultados['render'] = ok

        elif step == 'register':
            hook = 'statement'
            step_register(pipeline, nicho, hook=hook)

    separator(f"✅ PIPELINE [{pipeline.upper()}] COMPLETADO")
    for k, v in resultados.items():
        print(f"  {k}: {v}")

    return resultados


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description='🌾 Granja Viral — Orquestador principal',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--pipeline', choices=['es', 'en', 'both'], default='es',
        help='Pipeline a ejecutar (default: es)'
    )
    parser.add_argument(
        '--steps', nargs='+', choices=ALL_STEPS,
        default=ALL_STEPS,
        help='Pasos a ejecutar (default: todos)'
    )
    parser.add_argument(
        '--nicho', type=str, default=None,
        help='Forzar un nicho específico (omite detección automática)'
    )
    parser.add_argument(
        '--texto-tts', type=str, default=None,
        help='Texto personalizado para TTS (omite generación de guión)'
    )
    parser.add_argument(
        '--skip-render', action='store_true',
        help='Omitir el paso de render (útil para probar capas 1-2)'
    )
    parser.add_argument(
        '--skip-checks', action='store_true',
        help='Omitir preflight checks'
    )
    parser.add_argument(
        '--detect-niche', action='store_true',
        help='Solo detectar nicho y salir'
    )
    parser.add_argument(
        '--analytics', action='store_true',
        help='Solo mostrar reporte de analytics y salir'
    )
    return parser.parse_args()


def main():
    separator("🌾 GRANJA VIRAL — SISTEMA DE CONTENIDO VIRAL")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Root:  {ROOT}\n")

    args = parse_args()

    # — Shortcuts —
    if args.analytics:
        pipelines = ['es', 'en'] if args.pipeline == 'both' else [args.pipeline]
        for p in pipelines:
            step_analytics(p)
        return

    if args.detect_niche:
        pipelines = ['es', 'en'] if args.pipeline == 'both' else [args.pipeline]
        for p in pipelines:
            nicho = step_detect(p, args.nicho)
            print(f"\n✅ [{p.upper()}] Nicho elegido: {nicho}")
        return

    # — Preflight —
    if not args.skip_checks:
        if not preflight_checks():
            log.warning("Algunos checks fallaron. Continuando de todos modos...")

    # — Pasos —
    steps = args.steps
    if args.skip_render and 'render' in steps:
        steps = [s for s in steps if s != 'render']
        log.info("Render omitido por --skip-render")

    # — Ejecutar —
    pipelines = ['es', 'en'] if args.pipeline == 'both' else [args.pipeline]

    for pipeline in pipelines:
        run_pipeline(
            pipeline=pipeline,
            steps=steps,
            nicho_override=args.nicho,
            tts_texto=args.texto_tts,
            skip_checks=args.skip_checks,
        )

    separator("🏁 EJECUCIÓN FINALIZADA")


if __name__ == '__main__':
    main()