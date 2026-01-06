import logging

# Configuracion de Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"), # Guarda errores en archivo
        logging.StreamHandler()           # Muestra en consola
    ]
)
logger = logging.getLogger(__name__)

# URL de LM Studio
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

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