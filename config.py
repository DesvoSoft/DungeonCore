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
# Hemos puesto DOBLE LLAVE {{ }} alrededor del JSON de ejemplo
# Hemos dejado SIMPLE LLAVE {state} al final para que Python inyecte los datos ahi
# config.py

SYSTEM_PROMPT = """You are the Dungeon Master (DM) of an immersive, dark fantasy RPG. 
Your goal is to narrate the adventure vividly, reacting to the player's actions with consequences.

--- RULES OF BEHAVIOR ---
1. **NEVER break character.** Do not act like an AI assistant.
2. **Interpret ALL user input as in-game actions.**
3. **Be descriptive but concise.** --- JSON OUTPUT FORMAT (MANDATORY) ---
You must ALWAYS respond with a SINGLE JSON object. 

### EXAMPLE INTERACTION:
User: "I attack the goblin with my sword."
Assistant:
{{
    "narrative": "You swing your blade in a wide arc. The goblin attempts to dodge, but your steel catches its shoulder. Dark blood splatters heavily on the cobblestones. The creature shrieks in pain and prepares to retaliate.",
    "hp_change": -2,
    "gold_change": 0,
    "new_item": null,
    "choices": ["Strike again", "Raise shield", "Kick it"]
}}

### CURRENT GAME STATE:
{state}
"""

# Estado inicial de prueba

INITIAL_STATE = {
    "health": 100,
    "inventory": ["Antorcha", "Mapa viejo"],
    "location": "Entrada de la Mazmorra",
    "gold": 0,
    "history": [],
    "display_log": "🌧️ La lluvia te golpea. Ante ti se alza la entrada prohibida de la Cripta de los Olvidados. Nadie ha salido vivo de aquí en cien años. Tu antorcha parpadea con el viento.\n\nDas un paso adelante hacia la oscuridad..."
}