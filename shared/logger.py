"""
logger.py — Logger centralizado de Granja Viral
Escribe en consola (con colores) y en archivo de log con timestamp.
"""
import logging
import os
import sys
from datetime import datetime

# ─── Setup ───────────────────────────────────────────────────────────────────
LOGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(
    LOGS_DIR,
    f"granja_{datetime.now().strftime('%Y%m%d')}.log"
)

# ─── Colores ANSI ────────────────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG:    '\033[90m',   # gris
        logging.INFO:     '\033[0m',    # blanco normal
        logging.WARNING:  '\033[33m',   # amarillo
        logging.ERROR:    '\033[31m',   # rojo
        logging.CRITICAL: '\033[35m',   # magenta
    }
    ICONS = {
        logging.DEBUG:    '🔧',
        logging.INFO:     '✅',
        logging.WARNING:  '⚠️ ',
        logging.ERROR:    '❌',
        logging.CRITICAL: '💥',
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        icon  = self.ICONS.get(record.levelno, '')
        ts    = datetime.now().strftime('%H:%M:%S')
        msg   = record.getMessage()
        return f"{color}[{ts}] {icon}  {msg}{self.RESET}"


def get_logger(name: str = 'granja') -> logging.Logger:
    """
    Retorna un logger con handlers de consola (coloreado) y archivo.
    Llamalo al inicio de cada módulo:
        from shared.logger import get_logger
        log = get_logger(__name__)
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # evitar duplicar handlers

    logger.setLevel(logging.DEBUG)

    # — Consola —
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)

    # — Archivo —
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(name)s — %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(fh)

    return logger


# ─── Instancia global por si se importa directo ──────────────────────────────
log = get_logger('granja')