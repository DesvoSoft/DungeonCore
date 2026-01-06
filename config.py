import logging
import sys

# URL de LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# --- CONFIGURACIÓN DE LOGGING ---
# 1. Forzamos la salida de consola a UTF-8 (Vital para Windows)
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # 2. Guardamos los logs en archivo con UTF-8 explícito
        logging.FileHandler("debug.log", encoding='utf-8'), 
        logging.StreamHandler(sys.stdout)           
    ]
)
logger = logging.getLogger(__name__)

# Prompt del Sistema (La "Biblia" del DM)
SYSTEM_PROMPT = """You are a Dungeon Master.
CRITICAL: You must ALWAYS respond in valid JSON format.
Structure:
{
    "narrative": "Story description...",
    "hp_change": 0,
    "gold_change": 0,
    "new_item": null,
    "choices": ["Option A", "Option B"]
}
Current State: {state}
"""