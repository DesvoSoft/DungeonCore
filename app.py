import dash
from dash import Input, Output, State, ctx, no_update
from config import logger
from game_logic import initialize_game, process_turn
from frontend.layout import build_layout
from frontend.components import render_stat_card

# --- CONFIGURACION ---
DEV_MODE = False 

external_scripts = [{'src': 'https://cdn.tailwindcss.com'}]

app = dash.Dash(__name__, 
                external_scripts=external_scripts,
                update_title=None)

app.title = "DungeonCore AI"
app.layout = build_layout() # <-- ¡Mira qué limpio!

# --- LOGIC HELPERS ---
def render_stats_panel(state):
    """Genera el contenido dinámico de los stats."""
    hp_color = "text-green-400" if state['health'] > 50 else "text-red-500"
    inv_count = len(state['inventory'])
    
    return [
        render_stat_card("📍", "Ubicación", state['location'], "text-blue-400"),
        render_stat_card("❤️", "Salud", f"{state['health']} / 100", hp_color),
        render_stat_card("💰", "Oro", str(state['gold']), "text-yellow-400"),
        render_stat_card("🎒", "Inventario", f"{inv_count} Items", "text-purple-400")
    ]

# --- CALLBACKS PRINCIPALES ---
@app.callback(
    [Output("chat-display", "value"),
     Output("stats-bar", "children"),
     Output("user-input", "value"),
     Output("game-store", "data"),
     Output("dev-mode-indicator", "children"),
     Output("loading-trigger", "children")], 
    [Input("send-btn", "n_clicks"),
     Input("user-input", "n_submit"),
     Input("reset-btn", "n_clicks")],
    [State("user-input", "value"),
     State("game-store", "data"),
     State("chat-display", "value")]
)
def main_game_loop(btn_click, enter_submit, reset_click, user_text, current_state, current_chat_text):
    trigger = ctx.triggered_id
    dev_msg = f"🛠️ MOCK: {'ON' if DEV_MODE else 'OFF'}"
    
    # A. Inicialización / Reset
    if not current_state or trigger == "reset-btn":
        logger.info("Iniciando nueva partida...")
        new_state = initialize_game()
        return new_state['display_log'], render_stats_panel(new_state), "", new_state, dev_msg, ""

    # B. Turno del Jugador
    if (trigger == "send-btn" or trigger == "user-input") and user_text:
        new_state, turn_text = process_turn(user_text, current_state, mock=DEV_MODE)
        full_log = (current_chat_text or "") + turn_text
        new_state['display_log'] = full_log 
        return full_log, render_stats_panel(new_state), "", new_state, dev_msg, ""

    return no_update, no_update, no_update, no_update, dev_msg, no_update

if __name__ == "__main__":
    app.run(debug=True, port=8050)