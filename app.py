import dash
from dash import html, dcc, Input, Output, State, ctx, no_update, clientside_callback
from config import logger
from game_logic import initialize_game, process_turn, save_game_state, load_game_state
from frontend.layout import build_layout
from frontend.components import render_stat_card_simple, render_health_bar

# --- CONFIGURACION ---
DEV_MODE = False 

# Importante: Añadimos la librería de tipografía 'prose' de Tailwind
external_scripts = [
    {'src': 'https://cdn.tailwindcss.com?plugins=typography'} 
]

app = dash.Dash(__name__, 
                external_scripts=external_scripts,
                update_title=None)

app.title = "DungeonCore AI"
app.layout = build_layout()

# --- LOGIC HELPERS ---
def render_stats_panel(state):
    """Genera el contenido dinámico de los stats usando la nueva Barra de Vida."""
    inv_count = len(state['inventory'])
    
    return [
        # Tarjeta 1: Ubicación
        render_stat_card_simple("📍", "Ubicación", state['location'], "text-blue-400"),
        
        # Tarjeta 2: BARRA DE VIDA
        html.Div([
            render_health_bar(state['health'])
        ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800 col-span-1"),

        # Tarjeta 3: Oro
        render_stat_card_simple("💰", "Oro", str(state['gold']), "text-yellow-400"),
        
        # Tarjeta 4: Inventario
        render_stat_card_simple("🎒", "Mochila", f"{inv_count} Items", "text-purple-400")
    ]

# --- JAVASCRIPT: AUTO-SCROLL ---
clientside_callback(
    """
    function(children) {
        var chatBox = document.getElementById('chat-scroll-box');
        if(chatBox) {
            setTimeout(function() {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-scroll-box", "className"), 
    Input("chat-display", "children")
)

# --- CALLBACKS PRINCIPALES ---
@app.callback(
    [Output("chat-display", "children"),
     Output("stats-bar", "children"),
     Output("user-input", "value"),
     Output("game-store", "data"),
     Output("dev-mode-indicator", "children"),
     Output("loading-trigger", "children")], 
    [Input("send-btn", "n_clicks"),
     Input("user-input", "n_submit"),
     Input("reset-btn", "n_clicks"),
     Input("save-btn", "n_clicks"),
     Input("load-btn", "n_clicks")],
    [State("user-input", "value"),
     State("game-store", "data"),
     State("chat-display", "children")]
)
def main_game_loop(btn_click, enter_submit, reset_click, save_click, load_click, user_text, current_state, current_chat_children):
    trigger = ctx.triggered_id
    dev_msg = f"🛠️ MOCK: {'ON' if DEV_MODE else 'OFF'}"
    
    current_log_text = current_chat_children if isinstance(current_chat_children, str) else ""
    if not current_log_text: 
        current_log_text = ""

    # A. Inicialización / Reset
    if not current_state or trigger == "reset-btn":
        logger.info("Iniciando nueva partida...")
        new_state = initialize_game()
        return new_state['display_log'], render_stats_panel(new_state), "", new_state, dev_msg, ""

    # B. Guardar Partida
    if trigger == "save-btn":
        success, msg = save_game_state(current_state)
        updated_log = current_log_text + f"\n\n**💾 SISTEMA:** {msg}"
        current_state['display_log'] = updated_log
        return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, ""

    # C. Cargar Partida
    if trigger == "load-btn":
        loaded_state, msg = load_game_state()
        if loaded_state:
            return loaded_state['display_log'], render_stats_panel(loaded_state), "", loaded_state, dev_msg, ""
        else:
            updated_log = current_log_text + f"\n\n**⚠️ SISTEMA:** {msg}"
            return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, ""

    # D. Turno del Jugador
    if (trigger == "send-btn" or trigger == "user-input") and user_text:
        new_state, turn_text = process_turn(user_text, current_state, mock=DEV_MODE)
        
        turn_text_md = turn_text.replace("👤 TÚ:", "\n> **👤 TÚ:**").replace("🎲 DM:", "\n**🎲 DM:**")
        
        full_log = current_log_text + turn_text_md
        new_state['display_log'] = full_log 
        
        return full_log, render_stats_panel(new_state), "", new_state, dev_msg, ""

    return no_update, no_update, no_update, no_update, dev_msg, no_update

if __name__ == "__main__":
    app.run(debug=True, port=8050)