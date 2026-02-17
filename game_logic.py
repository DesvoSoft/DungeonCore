import json
import os
import random
from datetime import datetime
from config import logger, MAX_GOLD, MAX_INVENTORY, MAX_LEVEL, MAX_HEALTH_BASE, MAX_HEALTH_PER_LEVEL
from config import XP_TABLE, get_xp_for_level, get_next_level_xp, ENEMY_TEMPLATES, COMBAT_MECHANICS, ITEM_TEMPLATES
from ai_engine import query_dm

SAVE_DIR = "savegames"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_save_path(slot):
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")

def initialize_game():
    return {
        "health": MAX_HEALTH_BASE,
        "max_health": MAX_HEALTH_BASE,
        "level": 1,
        "xp": 0,
        "gold": 0,
        "inventory": ["Antorcha", "Espada oxidada"],
        "equipment": {
            "weapon": "Espada oxidada",
            "armor": None,
            "shield": None
        },
        "location": "Entrada de la Mazmorra",
        "status": "exploring",
        "history": [],
        "combat": {
            "active": False,
            "enemy_name": None,
            "enemy_hp": 0,
            "enemy_max_hp": 0,
            "enemy_type": None,
            "last_roll": None,
            "last_damage": None,
            "enemy_damage": None
        },
        "effects": {
            "poisoned": False,
            "bleeding": False,
            "blinded": False
        },
        "game_over": False,
        "death_count": 0,
        "total_kills": 0,
        "playtime_seconds": 0,
        "created_at": datetime.now().isoformat(),
        "last_played": datetime.now().isoformat(),
        "display_log": "🌧️ **PRÓLOGO**\n\nHas llegado a la entrada de la Cripta de los Lamentos. La lluvia golpea tu armadura oxidada y el viento aúlla como un lobo herido.\n\nNadie ha salido vivo de aquí en cien años.\n\n*Usa /ayuda para ver comandos disponibles.*\n\n¿Qué haces?"
    }

def get_equipment_bonus(state):
    weapon_bonus = 0
    armor_bonus = 0
    
    weapon = state.get("equipment", {}).get("weapon")
    if weapon:
        for item_key, item_data in ITEM_TEMPLATES.items():
            if item_data.get("name") == weapon and item_data.get("type") == "weapon":
                weapon_bonus = item_data.get("damage_bonus", 0)
                break
    
    armor = state.get("equipment", {}).get("armor")
    if armor:
        for item_key, item_data in ITEM_TEMPLATES.items():
            if item_data.get("name") == armor and item_data.get("type") == "armor":
                armor_bonus = item_data.get("ac_bonus", 0)
                break
    
    return weapon_bonus, armor_bonus

def spawn_enemy(enemy_type=None):
    if enemy_type is None:
        enemy_type = random.choice(list(ENEMY_TEMPLATES.keys()))
    
    template = ENEMY_TEMPLATES[enemy_type]
    return {
        "type": enemy_type,
        "name": template["name"],
        "hp": template["hp"],
        "max_hp": template["hp"],
        "damage_min": template["damage"][0],
        "damage_max": template["damage"][1],
        "xp_reward": template["xp_reward"],
        "gold_min": template["gold_reward"][0],
        "gold_max": template["gold_reward"][1],
        "description": template["description"]
    }

def calculate_player_attack(state):
    weapon_bonus, _ = get_equipment_bonus(state)
    level_bonus = (state.get("level", 1) - 1) // 2
    
    d20_roll = random.randint(1, 20)
    total_bonus = weapon_bonus + level_bonus
    total_roll = d20_roll + total_bonus
    
    return {
        "d20": d20_roll,
        "bonus": total_bonus,
        "total": total_roll,
        "crit": d20_roll == 20
    }

def calculate_damage(attack_result, state):
    weapon_bonus, _ = get_equipment_bonus(state)
    level_bonus = (state.get("level", 1) - 1) // 2
    
    base_damage = random.randint(1, 8)
    total_damage = base_damage + weapon_bonus + level_bonus
    
    if attack_result["crit"]:
        total_damage *= COMBAT_MECHANICS["crit_multiplier"]
    
    return total_damage

def calculate_enemy_attack(enemy):
    damage = random.randint(enemy["damage_min"], enemy["damage_max"])
    return damage

def check_level_up(state):
    current_level = state.get("level", 1)
    current_xp = state.get("xp", 0)
    
    if current_level >= MAX_LEVEL:
        return False, current_level
    
    xp_needed = get_xp_for_level(current_level + 1)
    if current_xp >= xp_needed:
        return True, current_level + 1
    
    return False, current_level

def apply_level_up(state, new_level):
    old_level = state["level"]
    state["level"] = new_level
    state["max_health"] = MAX_HEALTH_BASE + ((new_level - 1) * MAX_HEALTH_PER_LEVEL)
    state["health"] = state["max_health"]
    
    return f"🎉 ¡SUBISTE DE NIVEL! Nivel {old_level} → {new_level}\n+10 HP Máx | +1 Daño base"

def resolve_combat(user_action, state):
    combat = state.get("combat", {})
    if not combat.get("active"):
        return None
    
    action_lower = user_action.lower()
    attack_keywords = ["atacar", "golpear", "cortar", "attack", "hit", "slash", "stab", "luchar", "empujar"]
    defend_keywords = ["defender", "bloquear", "escudar", "defend", "block"]
    use_keywords = ["usar", "beber", "comer", "use", "drink", "eat"]
    flee_keywords = ["huir", "escapar", "run", "flee", "escape"]
    
    enemy = {
        "name": combat.get("enemy_name"),
        "hp": combat.get("enemy_hp"),
        "max_hp": combat.get("enemy_max_hp"),
        "damage_min": 3,
        "damage_max": 8
    }
    
    for etype, template in ENEMY_TEMPLATES.items():
        if template["name"] == enemy["name"]:
            enemy["damage_min"] = template["damage"][0]
            enemy["damage_max"] = template["damage"][1]
            break
    
    combat_result = {
        "player_action": None,
        "player_hit": False,
        "player_damage": 0,
        "player_crit": False,
        "enemy_action": None,
        "enemy_damage": 0,
        "enemy_dead": False,
        "combat_ended": False,
        "message": ""
    }
    
    if any(word in action_lower for word in attack_keywords):
        attack = calculate_player_attack(state)
        combat["last_roll"] = attack["total"]
        
        ac = COMBAT_MECHANICS["base_ac"]
        
        if attack["total"] >= ac:
            combat_result["player_hit"] = True
            combat_result["player_crit"] = attack["crit"]
            damage = calculate_damage(attack, state)
            combat_result["player_damage"] = damage
            combat["enemy_hp"] -= damage
            
            if attack["crit"]:
                combat_result["message"] = f"🎯 **CRÍTICO!** ({attack['d20']}+{attack['bonus']}) | Daño: {damage}"
            else:
                combat_result["message"] = f"⚔️ Golpe ({attack['d20']}+{attack['bonus']}) | Daño: {damage}"
            
            if combat["enemy_hp"] <= 0:
                combat["enemy_hp"] = 0
                combat_result["enemy_dead"] = True
                combat_result["combat_ended"] = True
                
                xp_reward = 0
                for etype, template in ENEMY_TEMPLATES.items():
                    if template["name"] == combat.get("enemy_name"):
                        xp_reward = template["xp_reward"]
                        gold_min = template["gold_reward"][0]
                        gold_max = template["gold_reward"][1]
                        gold_gained = random.randint(gold_min, gold_max)
                        combat_result["gold_gained"] = gold_gained
                        combat_result["xp_gained"] = xp_reward
                        state["total_kills"] = state.get("total_kills", 0) + 1
                        break
        else:
            combat_result["message"] = f"❌ Fallaste ({attack['d20']}+{attack['bonus']} < CA {ac})"
        
        combat_result["player_action"] = "attack"
    
    elif any(word in action_lower for word in defend_keywords):
        combat_result["player_action"] = "defend"
        combat_result["message"] = "🛡️ Te preparas para defenderte"
        enemy_damage = calculate_enemy_attack(enemy)
        enemy_damage = max(1, enemy_damage // 2)
        combat_result["enemy_damage"] = enemy_damage
    
    elif any(word in action_lower for word in flee_keywords):
        combat_result["player_action"] = "flee"
        if random.randint(1, 20) >= 10:
            combat_result["combat_ended"] = True
            combat_result["message"] = "🏃 Logras huir del combate"
        else:
            enemy_damage = calculate_enemy_attack(enemy)
            combat_result["enemy_damage"] = enemy_damage
            combat_result["message"] = f"❌ No logras huir! El enemigo te ataca: {enemy_damage} daño"
    
    else:
        enemy_damage = calculate_enemy_attack(enemy)
        combat_result["enemy_damage"] = enemy_damage
        combat_result["message"] = f"⚠️ Acción no reconocida. El {enemy['name']} te ataca: {enemy_damage} daño"
    
    if not combat_result["combat_ended"] and combat_result["enemy_damage"] > 0:
        combat["enemy_damage"] = combat_result["enemy_damage"]
    
    state["combat"] = combat
    return combat_result

def use_item(item_name, state):
    item_found = None
    item_key = None
    
    for ik, item_data in ITEM_TEMPLATES.items():
        if item_data["name"].lower() == item_name.lower():
            item_found = item_data
            item_key = ik
            break
    
    if not item_found:
        return None, "No tienes ese objeto"
    
    if item_found["name"] not in state.get("inventory", []):
        return None, "No tienes ese objeto en el inventario"
    
    effect = item_found.get("effect")
    result_message = ""
    
    if effect == "heal":
        heal_amount = item_found.get("value", 0)
        old_health = state["health"]
        state["health"] = min(state["max_health"], state["health"] + heal_amount)
        actual_heal = state["health"] - old_health
        result_message = f"💚 Te curas {actual_heal} puntos de vida"
        state["inventory"].remove(item_found["name"])
    
    elif effect == "cure_poison":
        if state.get("effects", {}).get("poisoned"):
            state["effects"]["poisoned"] = False
            result_message = "🧪 Has sido curado del envenenamiento"
            state["inventory"].remove(item_found["name"])
        else:
            return None, "No estás envenenado"
    
    elif effect == "escape":
        if state.get("combat", {}).get("active"):
            state["combat"]["active"] = False
            state["combat"]["enemy_name"] = None
            state["combat"]["enemy_hp"] = 0
            result_message = "💨 Huye del combate usando la bomba de humo"
            state["inventory"].remove(item_found["name"])
        else:
            return None, "No estás en combate"
    
    elif item_found.get("type") == "weapon":
        old_weapon = state["equipment"]["weapon"]
        state["equipment"]["weapon"] = item_found["name"]
        if old_weapon:
            state["inventory"].append(old_weapon)
        state["inventory"].remove(item_found["name"])
        result_message = f"⚔️ Equipaste: {item_found['name']}"
    
    elif item_found.get("type") == "armor":
        old_armor = state["equipment"]["armor"]
        state["equipment"]["armor"] = item_found["name"]
        if old_armor:
            state["inventory"].append(old_armor)
        state["inventory"].remove(item_found["name"])
        result_message = f"🛡️ Equipaste: {item_found['name']}"
    
    else:
        return None, "No puedes usar ese objeto así"
    
    return item_found["name"], result_message

def process_turn(user_input, current_state, mock=False):
    if current_state.get("game_over"):
        return current_state, "\n\n⚰️ **HAS MUERTO**\n\nUsa el botón de reiniciar para empezar de nuevo."
    
    user_input = user_input.strip()[:500]
    system_override_msg = ""
    item_used = None
    combat_result = None
    
    if user_input.lower().startswith("/ayuda") or user_input.lower() == "/help":
        help_text = """
📖 **COMANDOS DISPONIBLES:**

- `/generar [tipo]` - Invoca un enemigo (goblin, skeleton, orc, troll, etc.)
- `/estado` - Muestra tu estado actual
- `/historia` - Repite la historia del personaje
- `usar [objeto]` - Usa un objeto del inventario
- `equipar [objeto]` - Equipa un objeto
- `atacar`, `defender`, `huir` - Acciones de combate
"""
        current_state["history"].append({"role": "user", "content": user_input})
        current_state["history"].append({"role": "assistant", "content": help_text})
        return current_state, f"\n👤 TÚ: {user_input}\n{help_text}"
    
    if user_input.lower().startswith("/generar ") or user_input.lower().startswith("/spawn "):
        enemy_type = user_input.lower().split()[-1]
        if enemy_type not in ENEMY_TEMPLATES:
            enemy_type = None
        
        if not current_state.get("combat", {}).get("active"):
            enemy = spawn_enemy(enemy_type)
            current_state["combat"]["active"] = True
            current_state["combat"]["enemy_name"] = enemy["name"]
            current_state["combat"]["enemy_hp"] = enemy["hp"]
            current_state["combat"]["enemy_max_hp"] = enemy["max_hp"]
            current_state["combat"]["enemy_type"] = enemy["type"]
            system_override_msg = f"[SISTEMA]: ¡Un {enemy['name']} aparece! HP: {enemy['hp']}\nDescripción: {enemy['description']}"
        else:
            system_override_msg = "[SISTEMA]: ¡Ya estás en combate!"
    
    elif user_input.lower().startswith("/estado") or user_input.lower() == "/stats":
        stats = f"""
📊 **ESTADO DEL PERSONAJE**
- Nivel: {current_state['level']}
- XP: {current_state['xp']}/{get_next_level_xp(current_state['level']) or 'MAX'}
- Salud: {current_state['health']}/{current_state['max_health']}
- Oro: {current_state['gold']}
- Enemigos derrotados: {current_state.get('total_kills', 0)}
- Muertes: {current_state.get('death_count', 0)}
- Equipo: {current_state['equipment']['weapon'] or 'Ninguno'}
"""
        current_state["history"].append({"role": "user", "content": user_input})
        current_state["history"].append({"role": "assistant", "content": stats})
        return current_state, f"\n👤 TÚ: {user_input}\n{stats}"
    
    elif user_input.lower().startswith("usar ") or user_input.lower().startswith("use "):
        item_name = user_input[5:].strip()
        used, msg = use_item(item_name, current_state)
        if used:
            item_used = used
            system_override_msg = f"[SISTEMA]: {msg}"
        else:
            system_override_msg = f"[SISTEMA]: {msg}"
    
    elif user_input.lower().startswith("equipar ") or user_input.lower().startswith("equip "):
        item_name = user_input[8:].strip()
        used, msg = use_item(item_name, current_state)
        if used:
            item_used = used
            system_override_msg = f"[SISTEMA]: {msg}"
        else:
            system_override_msg = f"[SISTEMA]: {msg}"
    
    combat_result = resolve_combat(user_input, current_state)
    
    final_prompt = user_input
    if system_override_msg:
        final_prompt += f"\n\n{system_override_msg}"
    
    if combat_result:
        combat_context = combat_result["message"]
        if combat_result.get("enemy_dead"):
            gold_gained = combat_result.get("gold_gained", 0)
            xp_gained = combat_result.get("xp_gained", 0)
            combat_context += f"\n[SISTEMA]: ¡Derrotaste al enemigo! +{gold_gained} oro, +{xp_gained} XP"
            current_state["gold"] = min(MAX_GOLD, current_state["gold"] + gold_gained)
            current_state["xp"] += xp_gained
            
            leveled_up, new_level = check_level_up(current_state)
            if leveled_up:
                level_msg = apply_level_up(current_state, new_level)
                combat_context += f"\n{level_msg}"
        
        if combat_result.get("enemy_damage", 0) > 0:
            current_state["health"] -= combat_result["enemy_damage"]
        
        final_prompt += f"\n\n{combat_context}\n[INSTRUCCIÓN]: Narra el resultado del combate basándote en los números del sistema."
    
    ai_response = query_dm(final_prompt, current_state, mock)
    
    narrative = ai_response.get("narrative", "...")
    
    if not combat_result:
        hp_change = ai_response.get("hp_change", 0)
        gold_change = ai_response.get("gold_change", 0)
        
        hp_change = max(-20, min(50, hp_change))
        gold_change = max(-100, min(MAX_GOLD - current_state["gold"], gold_change))
        
        current_state["health"] += hp_change
        current_state["gold"] = max(0, min(MAX_GOLD, current_state["gold"] + gold_change))
    
    new_item = ai_response.get("new_item")
    if new_item and len(current_state.get("inventory", [])) < MAX_INVENTORY:
        if new_item not in current_state.get("inventory", []):
            current_state["inventory"].append(new_item)
    
    current_state["history"].append({"role": "user", "content": user_input})
    current_state["history"].append({"role": "assistant", "content": narrative})
    
    if len(current_state["history"]) > 20:
        current_state["history"] = current_state["history"][-20:]
    
    if current_state["health"] <= 0:
        current_state["health"] = 0
        current_state["game_over"] = True
        current_state["status"] = "dead"
        current_state["death_count"] = current_state.get("death_count", 0) + 1
        narrative += "\n\n⚰️ **HAS MUERTO**\n\nTu aventura termina aquí... por ahora.\n\n*Presiona 'Reiniciar' para comenzar de nuevo.*"
    
    current_state["last_played"] = datetime.now().isoformat()
    
    return current_state, f"\n\n👤 TÚ: {user_input}\n🎲 DM: {narrative}"

def save_game_state(state, slot=1):
    try:
        state["last_played"] = datetime.now().isoformat()
        save_path = get_save_path(slot)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        logger.info(f"Game saved to slot {slot}")
        return True, f"Partida guardada en Ranura {slot}"
    except Exception as e:
        logger.error(f"Save error: {e}")
        return False, f"Error al guardar: {str(e)}"

def load_game_state(slot=1):
    save_path = get_save_path(slot)
    if not os.path.exists(save_path):
        return None, f"No existe partida en Ranura {slot}"
    
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if "combat" not in state:
            state["combat"] = {"active": False}
        if "effects" not in state:
            state["effects"] = {"poisoned": False, "bleeding": False, "blinded": False}
        if "game_over" not in state:
            state["game_over"] = False
        if "death_count" not in state:
            state["death_count"] = 0
        if "total_kills" not in state:
            state["total_kills"] = 0
        
        logger.info(f"Game loaded from slot {slot}")
        state['display_log'] += f"\n\n📂 **Partida cargada** (Ranura {slot})"
        return state, f"Carga exitosa desde Ranura {slot}"
    except Exception as e:
        logger.error(f"Load error: {e}")
        return None, f"Error al cargar: {str(e)}"

def get_save_info(slot=1):
    save_path = get_save_path(slot)
    if not os.path.exists(save_path):
        return None
    
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return {
            "slot": slot,
            "level": state.get("level", 1),
            "location": state.get("location", "Unknown"),
            "health": state.get("health", 0),
            "max_health": state.get("max_health", 100),
            "last_played": state.get("last_played", "Unknown"),
            "game_over": state.get("game_over", False)
        }
    except:
        return None
