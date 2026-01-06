import json
import re
import requests
import time
from config import LM_STUDIO_URL, SYSTEM_PROMPT, logger

def clean_json_response(text):
    """Limpia el texto basura que las IAs suelen poner antes/después del JSON."""
    try:
        # Busca el primer '{' y el ultimo '}'
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    except Exception as e:
        logger.error(f"Error limpiando JSON: {e}")
        return text

def query_dm(user_input, current_state, mock=False):
    """
    Consulta al DM.
    Si mock=True, devuelve una respuesta falsa para testing rápido.
    """
    logger.info(f"Jugador dice: {user_input}")

    # --- MODO TESTING (MOCK) ---
    if mock:
        logger.info("⚠️ Usando MOCK AI (No conectando a LM Studio)")
        time.sleep(0.5) # Simula latencia
        return {
            "narrative": f"[MOCK] Has dicho '{user_input}'. El sistema funciona.",
            "hp_change": -5,
            "gold_change": 10,
            "new_item": "Roca de Testeo",
            "choices": ["Seguir testeando", "Salir"]
        }

    # --- MODO REAL ---
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(state=str(current_state))},
        {"role": "user", "content": user_input}
    ]

    try:
        response = requests.post(
            LM_STUDIO_URL, 
            json={"model": "local-model", "messages": messages, "temperature": 0.7},
            timeout=10
        )
        response.raise_for_status()
        
        raw_content = response.json()["choices"][0]["message"]["content"]
        logger.debug(f"Respuesta Raw de IA: {raw_content}")

        cleaned_json = clean_json_response(raw_content)
        data = json.loads(cleaned_json)
        
        return data

    except json.JSONDecodeError:
        logger.error("La IA no devolvió un JSON válido.")
        return {
            "narrative": "El DM murmura cosas ininteligibles (Error de JSON).",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }
    except requests.exceptions.ConnectionError:
        logger.critical("No se pudo conectar a LM Studio.")
        return {
            "narrative": "Parece que el servidor del universo está apagado (Connection Error).",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }