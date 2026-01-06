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
        time.sleep(1) # Simula latencia un poco más realista
        return {
            "narrative": f"[MOCK] Has intentado '{user_input}'. El sistema detecta tu intención y calcula las consecuencias...",
            "hp_change": -5,
            "gold_change": 10,
            "new_item": "Roca de Debug",
            "choices": ["Seguir probando", "Reiniciar"]
        }

    # --- MODO REAL ---
    
    # 1. INYECCIÓN DE ESTILO (El truco para que no parezca un Chatbot)
    # Envolvemos lo que dice el usuario con instrucciones ocultas para la IA.
    style_injection = f"""
    [Player Action]: "{user_input}"
    
    [Instruction]: Narrate the immediate consequence of this action in the style of a dark fantasy RPG. 
    Interpreta the input as an in-game character action, NOT a conversation with an assistant.
    If the input is vague (like "Hello"), interpret it as the character shouting.
    """

    # 2. CONSTRUCCIÓN DEL MENSAJE
    messages = [
        # A. Prompt del Sistema (Las reglas del juego)
        {"role": "system", "content": SYSTEM_PROMPT.format(state=str(current_state))}
    ]
    
    # B. Historial (Memoria de corto plazo)
    # Añadimos los últimos 6 turnos para que no olvide el contexto inmediato
    history = current_state.get("history", [])
    if history:
        messages.extend(history[-6:])
        
    # C. Acción Actual (Con la inyección de estilo)
    messages.append({"role": "user", "content": style_injection})

    try:
        response = requests.post(
            LM_STUDIO_URL, 
            json={
                "model": "local-model", 
                "messages": messages, 
                "temperature": 0.8,  # Más creatividad (menos robótico)
                "max_tokens": 800    # Permitimos respuestas un poco más largas
            },
            timeout=45 # Aumentado a 45s para evitar errores de espera en GPUs lentas
        )
        response.raise_for_status()
        
        raw_content = response.json()["choices"][0]["message"]["content"]
        logger.debug(f"Respuesta Raw de IA: {raw_content}")

        cleaned_json = clean_json_response(raw_content)
        data = json.loads(cleaned_json)
        
        return data

    except json.JSONDecodeError:
        logger.error("La IA no devolvió un JSON válido.")
        # Fallback suave: Mostramos el texto crudo como narrativa si falla el JSON
        return {
            "narrative": f"El DM narra algo confuso:\n\n{raw_content}",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }
    except requests.exceptions.Timeout:
        logger.error("Timeout: La IA tardó demasiado en responder.")
        return {
            "narrative": "⏳ El Dungeon Master se ha quedado pensando demasiado tiempo (Timeout). Intenta una acción más simple.",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }
    except requests.exceptions.ConnectionError:
        logger.critical("No se pudo conectar a LM Studio.")
        return {
            "narrative": "❌ Error de Conexión: Asegúrate de que LM Studio tiene el servidor iniciado en el puerto 1234.",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {
            "narrative": "Un error arcano ha ocurrido en el motor de realidad.",
            "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
        }