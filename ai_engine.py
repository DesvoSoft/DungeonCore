import json
import requests
import time
import json_repair
from config import LM_STUDIO_URL, SYSTEM_PROMPT, logger, MAX_LEVEL, get_next_level_xp
from config import MAX_HEALTH_BASE, MAX_HEALTH_PER_LEVEL, MAX_GOLD

MAX_INPUT_LENGTH = 500
MAX_HISTORY_ITEMS = 10

def sanitize_input(user_input):
    if not user_input:
        return ""
    sanitized = user_input.strip()[:MAX_INPUT_LENGTH]
    sanitized = sanitized.replace("\x00", "")
    return sanitized

def build_context_string(state):
    level = state.get("level", 1)
    health = state.get("health", 0)
    max_health = state.get("max_health", MAX_HEALTH_BASE)
    gold = state.get("gold", 0)
    location = state.get("location", "Unknown")
    inventory = state.get("inventory", [])
    equipment = state.get("equipment", {})
    status = state.get("status", "exploring")
    combat = state.get("combat", {})
    
    equipment_str = f"Arma: {equipment.get('weapon', 'Ninguna')} | Armadura: {equipment.get('armor', 'Ninguna')} | Escudo: {equipment.get('shield', 'Ninguno')}"
    
    combat_info = ""
    if combat.get("active"):
        combat_info = f"""
--- COMBATE ACTIVO ---
- Enemigo: {combat.get('enemy_name', 'Unknown')}
- HP Enemigo: {combat.get('enemy_hp', 0)}/{combat.get('enemy_max_hp', 0)}
- Último dado: {combat.get('last_roll', 'N/A')}
"""
    
    effects = state.get("effects", {})
    status_effects = []
    if effects.get("poisoned"):
        status_effects.append("Envenenado")
    if effects.get("bleeding"):
        status_effects.append("Sangrando")
    if effects.get("blinded"):
        status_effects.append("Ceguera")
    
    if status_effects:
        status += f" | Afcciones: {', '.join(status_effects)}"
    
    return f"""
Nivel: {level}
Salud: {health}/{max_health}
Oro: {gold}
Ubicación: {location}
Inventario: {', '.join(inventory) if inventory else 'Vacío'}
Equipo: {equipment_str}
Estado: {status}
{combat_info}
"""

def query_dm(user_input, current_state, mock=False):
    logger.info(f"Player action: {user_input}")
    
    user_input = sanitize_input(user_input)
    
    if mock:
        time.sleep(0.5)
        return {
            "narrative": f"[MOCK] You acted: '{user_input}'. The system is running in DEV_MODE.",
            "hp_change": 0,
            "gold_change": 0,
            "new_item": None,
            "item_used": None,
            "combat_ended": False,
            "level_up": False,
            "xp_gained": 0,
            "choices": ["Continuar", "Explorar"]
        }
    
    state_context = build_context_string(current_state)
    
    level = current_state.get("level", 1)
    health = current_state.get("health", 0)
    max_health = current_state.get("max_health", MAX_HEALTH_BASE)
    gold = current_state.get("gold", 0)
    location = current_state.get("location", "Unknown")
    inventory = current_state.get("inventory", [])
    equipment = current_state.get("equipment", {})
    status = current_state.get("status", "exploring")
    
    weapon = equipment.get("weapon", "Espada oxidada")
    armor = equipment.get("armor", "Ninguna")
    shield = equipment.get("shield", "Ninguno")
    equipment_str = f"Arma: {weapon} | Armadura: {armor} | Escudo: {shield}"
    
    formatted_prompt = SYSTEM_PROMPT.format(
        level=level,
        health=health,
        max_health=max_health,
        gold=gold,
        location=location,
        inventory=", ".join(inventory) if inventory else "Vacío",
        equipment=equipment_str,
        status=status,
        state=state_context
    )
    
    messages = [
        {"role": "system", "content": formatted_prompt},
    ]
    
    history = current_state.get("history", [])
    if history:
        messages.extend(history[-MAX_HISTORY_ITEMS:])
    
    style_injection = f"""
[Acción del Jugador]: "{user_input}"

[Instrucción]: Eres el Narrador. Narra la consecuencia inmediata de esta acción en ESPAÑOL.
OBLIGATORIO: Responde SOLAMENTE con el objeto JSON.
"""
    
    messages.append({"role": "user", "content": style_injection})
    
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}...")
            
            response = requests.post(
                LM_STUDIO_URL, 
                json={
                    "model": "local-model", 
                    "messages": messages, 
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=60
            )
            response.raise_for_status()
            
            raw_content = response.json()["choices"][0]["message"]["content"]
            logger.debug(f"AI Raw Response (Attempt {attempt+1}): {raw_content[:200]}...")
            
            decoded_object = json_repair.loads(raw_content)
            
            if "narrative" not in decoded_object:
                raise ValueError("Parsed JSON missing 'narrative' field")
            
            return decoded_object

        except requests.exceptions.ConnectionError:
            logger.critical("Connection Error: Is LM Studio running on port 1234?")
            return {
                "narrative": "❌ **Error de Conexión:** No se pudo alcanzar el servidor de IA. ¿Está LM Studio ejecutándose en el puerto 1234?",
                "hp_change": 0,
                "gold_change": 0,
                "new_item": None,
                "item_used": None,
                "combat_ended": False,
                "level_up": False,
                "xp_gained": 0,
                "choices": []
            }
            
        except Exception as e:
            logger.warning(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                time.sleep(1.5)
            else:
                logger.error("All retries failed.")
                return {
                    "narrative": f"**[ERROR DEL SISTEMA]** El Dungeon Master está confuse y no pudo procesar tu acción.\n\n*Info de depuración:* {str(e)}",
                    "hp_change": 0,
                    "gold_change": 0,
                    "new_item": None,
                    "item_used": None,
                    "combat_ended": False,
                    "level_up": False,
                    "xp_gained": 0,
                    "choices": ["Intentar de nuevo"]
                }
