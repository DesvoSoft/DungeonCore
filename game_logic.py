import json
import os
import random
from datetime import datetime
from config import logger
from ai_engine import query_dm

SAVE_FILE = "savegame.json"

def initialize_game():
    """
    Creates the initial state of the game.
    """
    return {
        "location": "Entrada de la Mazmorra",
        "health": 100,
        "max_health": 100,
        "gold": 0,
        "inventory": ["Antorcha", "Espada oxidada"],
        
        # --- NEW: COMBAT STATE ---
        "combat": {
            "active": False,
            "enemy_name": None,
            "enemy_hp": 0,
            "enemy_max_hp": 0,
            "last_roll": None
        },
        
        "history": [],
        "display_log": "Has llegado a la entrada de una mazmorra antigua. El aire es frio y huele a humedad..."
    }

# --- RNG & COMBAT MECHANICS ---

def spawn_random_enemy():
    """Generates a random enemy for testing mechanics."""
    enemies = [
        {"name": "Goblin Scavenger", "hp": 15},
        {"name": "Skeleton Warrior", "hp": 25},
        {"name": "Giant Rat", "hp": 10},
        {"name": "Dark Cultist", "hp": 20}
    ]
    mob = random.choice(enemies)
    return mob

def resolve_combat_mechanics(user_action, state):
    """
    Analyzes the user's text. If they are attacking and in combat,
    Python calculates the result (Hit/Miss/Damage).
    Returns a string of 'System Context' to guide the AI.
    """
    combat_state = state['combat']
    
    # 1. Check if combat is active
    if not combat_state['active']:
        return None

    # 2. Check keywords (Simple parser)
    action_lower = user_action.lower()
    attack_keywords = ["atacar", "golpear", "cortar", "attack", "hit", "slash", "stab", "luchar"]
    
    if any(word in action_lower for word in attack_keywords):
        enemy_name = combat_state['enemy_name']
        
        # 3. RNG: D20 Roll
        d20_roll = random.randint(1, 20)
        state['combat']['last_roll'] = d20_roll
        
        # Threshold to hit (AC). Simplified to 11 for now.
        ac_threshold = 11 
        
        context_msg = ""
        
        if d20_roll >= ac_threshold:
            # HIT: Calculate Damage (1d8 + 2)
            damage = random.randint(1, 8) + 2
            
            # Critical Hit Logic
            if d20_roll == 20:
                damage = damage * 2
                context_msg = f"[SYSTEM]: CRITICAL HIT! (Rolled 20). Dealt {damage} damage."
            else:
                context_msg = f"[SYSTEM]: HIT! (Rolled {d20_roll}). Dealt {damage} damage."
            
            # Apply damage
            combat_state['enemy_hp'] -= damage
            
            # Check Death
            if combat_state['enemy_hp'] <= 0:
                combat_state['enemy_hp'] = 0
                combat_state['active'] = False
                context_msg += f" The {enemy_name} takes fatal damage and DIES. Combat ended."
            else:
                context_msg += f" The {enemy_name} has {combat_state['enemy_hp']} HP remaining."
        else:
            # MISS
            context_msg = f"[SYSTEM]: MISS! (Rolled {d20_roll}). The attack fails to connect with the {enemy_name}."
            
        return context_msg
    
    return None

# --- MAIN LOOP ---

def process_turn(user_input, current_state, mock=False):
    """
    Main game loop:
    1. Check for debug commands (Spawn).
    2. Calculate mechanics (Python).
    3. Send Context + User Input to AI.
    4. Update State with AI response.
    """
    
    # --- STEP 0: DEBUG COMMANDS (To test combat easily) ---
    system_override_msg = ""
    if "generar enemigo" in user_input.lower() or "spawn enemy" in user_input.lower():
        if not current_state['combat']['active']:
            mob = spawn_random_enemy()
            current_state['combat']['active'] = True
            current_state['combat']['enemy_name'] = mob['name']
            current_state['combat']['enemy_hp'] = mob['hp']
            current_state['combat']['enemy_max_hp'] = mob['hp']
            system_override_msg = f"[SYSTEM]: A wild {mob['name']} (HP: {mob['hp']}) appears! Combat started."
        else:
            system_override_msg = "[SYSTEM]: You are already in combat!"

    # --- STEP 1: RESOLVE MECHANICS ---
    # Python calculates math before the AI speaks
    mechanics_context = resolve_combat_mechanics(user_input, current_state)
    
    # Combine user input with system context for the Prompt
    final_prompt = user_input
    if system_override_msg:
        final_prompt += f"\n\n{system_override_msg}"
    if mechanics_context:
        final_prompt += f"\n\n{mechanics_context}\n[INSTRUCTION]: Narrate this combat outcome strictly based on the SYSTEM numbers provided."

    # --- STEP 2: QUERY AI ---
    ai_response = query_dm(final_prompt, current_state, mock)
    
    # --- STEP 3: UPDATE STATE ---
    # Update text log
    narrative = ai_response.get("narrative", "...")
    
    # Update Numeric Stats (Player HP/Gold) from AI decision
    # (The AI still decides if the monster hits back via the JSON hp_change)
    current_state['health'] += ai_response.get("hp_change", 0)
    current_state['gold'] += ai_response.get("gold_change", 0)
    
    # Health Cap handling
    if current_state['health'] > current_state['max_health']:
        current_state['health'] = current_state['max_health']
    
    # Inventory
    new_item = ai_response.get("new_item")
    if new_item and new_item not in current_state['inventory']:
        current_state['inventory'].append(new_item)
        
    # Append to history
    current_state['history'].append({"role": "user", "content": user_input})
    current_state['history'].append({"role": "assistant", "content": narrative})
    
    # Limit history size to avoid token overflow
    if len(current_state['history']) > 20:
        current_state['history'] = current_state['history'][-20:]

    return current_state, f"\n\n👤 TÚ: {user_input}\n🎲 DM: {narrative}"

# --- PERSISTENCE ---

def save_game_state(state):
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
        logger.info("Game saved.")
        return True, "Partida guardada correctamente."
    except Exception as e:
        logger.error(f"Save error: {e}")
        return False, f"Error al guardar: {str(e)}"

def load_game_state():
    if not os.path.exists(SAVE_FILE):
        return None, "No existe archivo de guardado."
    
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Backwards compatibility check
        if "combat" not in state:
            state["combat"] = {
                "active": False,
                "enemy_name": None,
                "enemy_hp": 0,
                "enemy_max_hp": 0
            }
            
        logger.info("Game loaded.")
        state['display_log'] += "\n\n📂 [SISTEMA] Partida cargada."
        return state, "Carga exitosa."
    except Exception as e:
        logger.error(f"Load error: {e}")
        return None, f"Error al cargar: {str(e)}"