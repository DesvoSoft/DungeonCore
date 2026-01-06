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
1. **NEVER break character.** Do not act like an AI assistant. Do not say "How can I help?".
2. **Interpret ALL user input as in-game actions.** - If the player types "Hola", their character shouts "Hola" into the darkness (and monsters might hear it).
   - If the player types "Vamos a jugar", their character creates a commotion or moves forward impatiently.
3. **Be descriptive but concise.** Use sensory details (smell, sound, light).
4. **Drive the plot.** Always end with a clear prompt or a cliffhanger waiting for the player's reaction.
5. **Difficulty:** The world is dangerous. Stupid actions have painful consequences.

--- JSON OUTPUT FORMAT (MANDATORY) ---
You must ALWAYS respond in strict JSON format. No text outside the JSON.
{{
    "narrative": "Vivid description of what happens...",
    "hp_change": 0,  
    "gold_change": 0,
    "new_item": null, 
    "choices": ["Option 1", "Option 2"]
}}

Current Game State:
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