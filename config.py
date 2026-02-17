import logging
import sys

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log", encoding='utf-8'), 
        logging.StreamHandler(sys.stdout)           
    ]
)
logger = logging.getLogger(__name__)

# --- GAME CONSTANTS ---
MAX_GOLD = 9999
MAX_INVENTORY = 10
MAX_LEVEL = 20
MAX_HEALTH_BASE = 100
MAX_HEALTH_PER_LEVEL = 10

XP_TABLE = {
    1: 0,
    2: 100,
    3: 175,
    4: 275,
    5: 400,
    6: 550,
    7: 725,
    8: 925,
    9: 1150,
    10: 1400,
    11: 1700,
    12: 2050,
    13: 2450,
    14: 2900,
    15: 3400,
    16: 3950,
    17: 4550,
    18: 5200,
    19: 5900,
    20: 6650
}

def get_xp_for_level(level):
    return XP_TABLE.get(level, XP_TABLE[MAX_LEVEL])

def get_next_level_xp(current_level):
    if current_level >= MAX_LEVEL:
        return None
    return XP_TABLE.get(current_level + 1, XP_TABLE[MAX_LEVEL])

ENEMY_TEMPLATES = {
    "goblin": {
        "name": "Goblin Escarbador",
        "hp": 15,
        "damage": (3, 6),
        "xp_reward": 15,
        "gold_reward": (1, 8),
        "description": "Una criatura baja y astuta con ojos amarillos."
    },
    "skeleton": {
        "name": "Esqueleto Guerrero",
        "hp": 25,
        "damage": (4, 8),
        "xp_reward": 25,
        "gold_reward": (5, 15),
        "description": "Los huesos de un guerrero olvidado, aún moviéndose."
    },
    "rat": {
        "name": "Rata Gigante",
        "hp": 10,
        "damage": (2, 5),
        "xp_reward": 8,
        "gold_reward": (0, 3),
        "description": "Del tamaño de un perro, con colmillos relucientes."
    },
    "cultist": {
        "name": "Cultista Oscuro",
        "hp": 30,
        "damage": (5, 10),
        "xp_reward": 35,
        "gold_reward": (10, 25),
        "description": "Encapuchado, murmura oraciones profanas."
    },
    "orc": {
        "name": "Orco Berserker",
        "hp": 45,
        "damage": (6, 12),
        "xp_reward": 50,
        "gold_reward": (15, 30),
        "description": "Masivo, con cicatrices de mil batallas."
    },
    "troll": {
        "name": "Troll de Roca",
        "hp": 60,
        "damage": (8, 15),
        "xp_reward": 75,
        "gold_reward": (25, 50),
        "description": "Una mole de piedra viviente con apetito voraz."
    },
    "wraith": {
        "name": "Espectro Vengativo",
        "hp": 35,
        "damage": (7, 12),
        "xp_reward": 60,
        "gold_reward": (20, 40),
        "description": "Una entidad fantasmal que drena la vida."
    },
    "dragon_whelp": {
        "name": "Dracónicedo",
        "hp": 80,
        "damage": (10, 18),
        "xp_reward": 100,
        "gold_reward": (50, 100),
        "description": "Una joven dragón con escamas negras."
    }
}

COMBAT_MECHANICS = {
    "base_ac": 12,
    "crit_threshold": 20,
    "crit_multiplier": 2
}

ITEM_TEMPLATES = {
    "pocion_vida": {
        "name": "Poción de Vida",
        "type": "consumible",
        "effect": "heal",
        "value": 25,
        "description": "Restaura 25 puntos de vida."
    },
    "pocion_vida_mayor": {
        "name": "Poción de Vida Mayor",
        "type": "consumible",
        "effect": "heal",
        "value": 50,
        "description": "Restaura 50 puntos de vida."
    },
    "antidoto": {
        "name": "Antídoto",
        "type": "consumible",
        "effect": "cure_poison",
        "value": 0,
        "description": "Cura el estado de envenenamiento."
    },
    "espada_rustica": {
        "name": "Espada Rústica",
        "type": "weapon",
        "damage_bonus": 1,
        "description": "Una espada oxidada pero funcional. +1 Daño."
    },
    "escudo_madera": {
        "name": "Escudo de Madera",
        "type": "armor",
        "ac_bonus": 1,
        "description": "Un escudo de madera reforzada. +1 CA."
    },
    "armadura_cuero": {
        "name": "Armadura de Cuero",
        "type": "armor",
        "ac_bonus": 2,
        "description": "Armadura ligera de cuero. +2 CA."
    },
    "bomba_humo": {
        "name": "Bomba de Humo",
        "type": "consumible",
        "effect": "escape",
        "value": 0,
        "description": "Permite escapar de cualquier combate."
    }
}

SYSTEM_PROMPT = """ERES EL DUNGEON MASTER (DM) DE UNA AVENTURA DE ROL DE FANTASÍA OSCURA Y LETAL.
TU OBJETIVO ES NARRAR UNA HISTORIA INMERSIVA Y EN ESPAÑOL.

--- CONTEXTO DEL JUGADOR ---
- **Nombre:** Aventurero
- **Nivel:** {level}
- **Salud:** {health}/{max_health}
- **Oro:** {gold}
- **Ubicación:** {location}
- **Inventario:** {inventory}
- **Equipo:** {equipment}
- **Estado:** {status}

--- REGLAS ABSOLUTAS ---
1. **IDIOMA:** SIEMPRE ESPAÑOL.
2. **NO PREGUNTES:** No preguntes "¿Qué quieres hacer?". NARRA las consecuencias.
3. **MUNDO LETAL:** El jugador puede morir. Describe consecuencias realistas.
4. **COMBATE:** Si el jugador está en combate:
   - El sistema ya calculó los dados (tú NO calculas daños)
   - Solo NARRAR el resultado: hit, miss, crit, muerte del enemigo
   - NO inventes números diferentes a los dados
5. **OBJETOS:** Si el jugador usa un objeto del inventario, el sistema procesó el efecto.
   - TÚ solo narrar lo que ocurre: "Bebes la poción..." o "El enemigo esquiva tu ataque..."
6. **XP Y NIVELES:** El sistema maneja la experiencia. NO menciones niveles excepto en momentos épicos.
7. **HISTORIA:** Construye sobre lo que ya ocurrió. No repitas descripciones.

--- FORMATO DE RESPUESTA (JSON OBLIGATORIO) ---
Responde ÚNICAMENTE con un objeto JSON válido.

Ejemplo:
{{
    "narrative": "Avanzas por el pasillo. De repente...",
    "hp_change": -5,
    "gold_change": 0,
    "new_item": null,
    "item_used": null,
    "combat_ended": false,
    "choices": ["Investigar", "Continuar", "Buscar salida"]
}}

--- CAMPOS DISPONIBLES ---
- narrative: (string) Tu narración en español
- hp_change: (int) Cambio de vida del jugador (-10 a +50 max)
- gold_change: (int) Oro ganado/perdido (0 a +100 max)
- new_item: (string|null) Item encontrado (si lo hay)
- item_used: (string|null) Item usado por el jugador
- combat_ended: (bool) true si el combate terminó
- level_up: (bool) true si el jugador sube de nivel
- xp_gained: (int) XP ganada (0-100 max)
- choices: (array) 2-4 opciones para el jugador

--- ESTADO ACTUAL ---
{state}
"""

INITIAL_STATE = {
    "health": 100,
    "max_health": 100,
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
        "last_damage": None
    },
    "effects": {
        "poisoned": False,
        "bleeding": False,
        "blinded": False
    },
    "display_log": "🌧️ **PRÓLOGO**\n\nHas llegado a la entrada de la Cripta de los Lamentos. La lluvia golpea tu armadura oxidada y el viento aúlla como un lobo herido.\n\nNadie ha salido vivo de aquí en cien años.\n\n*Usa /ayuda para ver comandos disponibles.*\n\n¿Qué haces?"
}
