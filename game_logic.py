from config import INITIAL_STATE, logger
from ai_engine import query_dm

def initialize_game():
    """Retorna el estado inicial limpio para una nueva partida."""
    # Hacemos una copia para no modificar la configuración original
    return INITIAL_STATE.copy()

def process_turn(user_input, current_state, mock=False):
    """
    Toma la acción del usuario, consulta a la IA y actualiza el estado.
    Retorna: (nuevo_estado, texto_para_mostrar)
    """
    
    # 1. Validación de Estado (Si ya murió, resetear o bloquear)
    if current_state.get('health', 0) <= 0:
        return current_state, "\n💀 Estás muerto. Presiona 'Nueva Partida'."

    # 2. Consultar al Motor de IA
    ai_data = query_dm(user_input, current_state, mock=mock)

    # 3. Actualizar Estadísticas (Matemáticas)
    # Usamos .get() para evitar errores si la IA olvida un campo
    hp_delta = ai_data.get('hp_change', 0)
    gold_delta = ai_data.get('gold_change', 0)
    
    current_state['health'] += hp_delta
    current_state['gold'] += gold_delta

    # Evitar vida negativa visualmente, aunque lógica ya sea muerte
    if current_state['health'] < 0:
        current_state['health'] = 0

    # 4. Gestión de Inventario
    new_item = ai_data.get('new_item')
    # Solo agregamos si existe y no es "None" o vacío
    if new_item and isinstance(new_item, str):
        # Evitamos duplicados exactos si quieres (opcional)
        if new_item not in current_state['inventory']:
            current_state['inventory'].append(new_item)
            logger.info(f"Ítem añadido: {new_item}")

    # 5. Actualizar Historial (Memoria de la IA)
    narrative = ai_data.get('narrative', '...')
    
    # Guardamos en el formato que la IA necesita leer en el futuro
    current_state['history'].append({"role": "user", "content": user_input})
    current_state['history'].append({"role": "assistant", "content": narrative})

    # Limitamos el historial a los últimos 10 turnos para no saturar la memoria (context window)
    if len(current_state['history']) > 20:
        current_state['history'] = current_state['history'][-20:]

    # 6. Formatear la respuesta visual para el usuario
    # Construimos el string que se verá en la pantalla azul del chat
    display_text = f"\n\n> 👤 TÚ: {user_input}\n🎲 DM: {narrative}"
    
    # Añadimos feedback visual de cambios numéricos
    changes = []
    if hp_delta != 0: changes.append(f"{hp_delta:+d} HP")
    if gold_delta != 0: changes.append(f"{gold_delta:+d} Oro")
    if new_item: changes.append(f"+{new_item}")
    
    if changes:
        display_text += f"\n   ({', '.join(changes)})"

    # 7. Verificar Muerte POST-DAÑO
    if current_state['health'] <= 0:
        display_text += "\n\n💀 HAS MUERTO. Tu aventura termina aquí."

    return current_state, display_text