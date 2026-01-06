import dash
from dash import html, dcc, Input, Output, State, ctx, no_update
from config import logger
from game_logic import initialize_game, process_turn

# --- CONFIGURACION ---
DEV_MODE = False 

# Script de Tailwind CDN
external_scripts = [
    {'src': 'https://cdn.tailwindcss.com'}
]

app = dash.Dash(__name__, 
                external_scripts=external_scripts,
                update_title=None)

app.title = "DungeonCore AI"

# --- LAYOUT CON TAILWIND ---
app.layout = html.Div([
    
    # Contenedor Principal (Centrado y con ancho máximo)
    html.Div([
        
        # 1. HEADER
        html.H1("🐉 DungeonCore", className="text-4xl md:text-5xl font-bold text-center text-red-500 mb-6 mt-8 tracking-wider"),

        # 2. BARRA DE ESTADO (Grid responsive)
        html.Div(id="stats-bar", className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-gray-900 p-4 rounded-xl border border-gray-800 shadow-lg"),

        # 3. ÁREA DE CHAT
        html.Div([
            dcc.Textarea(
                id="chat-display",
                readOnly=True,
                className="w-full h-[500px] bg-gray-950 text-gray-300 border border-gray-800 rounded-lg p-4 font-mono text-base focus:outline-none focus:border-red-500 transition-colors resize-none shadow-inner",
                style={'fontFamily': '"Fira Code", monospace'} 
            )
        ], className="mb-4 relative"),

        # 4. CONTROLES (Input + Botón en Flexbox)
        html.Div([
            dcc.Input(
                id="user-input", 
                type="text", 
                placeholder="¿Qué haces? (Ej: Atacar, Huir, Inventario...)", 
                autoFocus=True, 
                debounce=True,
                className="flex-grow bg-gray-800 text-white border border-gray-700 rounded-l-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all"
            ),
            html.Button(
                "ACTUAR", 
                id="send-btn", 
                n_clicks=0, 
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-r-lg transition-colors duration-200 uppercase tracking-wide"
            ),
        ], className="flex w-full mb-2 shadow-lg"),

        # 5. LOADING SPINNER
        html.Div([
            dcc.Loading(
                id="loading-spinner",
                type="dot",
                color="#ef4444", 
                children=html.Div(id="loading-trigger")
            )
        ], className="h-8 flex justify-center items-center mb-8"),

        # 6. FOOTER
        html.Div([
            html.Button(
                "🔄 Reiniciar Partida", 
                id="reset-btn", 
                n_clicks=0, 
                className="text-gray-500 hover:text-white text-sm border border-gray-700 hover:border-gray-500 px-4 py-2 rounded-full transition-all"
            ),
            html.Div(id="dev-mode-indicator", className="text-gray-600 text-xs mt-3 font-mono")
        ], className="text-center pb-8")

    ], className="max-w-4xl mx-auto px-4 min-h-screen flex flex-col justify-center"),
    
    # --- ¡AQUÍ ESTABA EL ERROR! FALTABA ESTA LÍNEA ---
    dcc.Store(id='game-store', storage_type='session') 

], className="bg-gray-950 min-h-screen text-gray-100") 

# --- CALLBACKS ---
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
    
    # Helper para renderizar los stats con Tailwind
    def render_stat_card(icon, label, value, color_class="text-white"):
        return html.Div([
            html.Span(icon, className="text-2xl mr-2"),
            html.Div([
                html.Div(label, className="text-xs text-gray-500 uppercase tracking-wider font-bold"),
                html.Div(value, className=f"text-lg font-bold {color_class}")
            ], className="flex flex-col")
        ], className="flex items-center justify-center bg-gray-800/50 p-2 rounded-lg")

    def render_stats_panel(state):
        hp_color = "text-green-400" if state['health'] > 50 else "text-red-500"
        inv_count = len(state['inventory'])
        
        return [
            render_stat_card("📍", "Ubicación", state['location'], "text-blue-400"),
            render_stat_card("❤️", "Salud", f"{state['health']} / 100", hp_color),
            render_stat_card("💰", "Oro", str(state['gold']), "text-yellow-400"),
            render_stat_card("🎒", "Inventario", f"{inv_count} Items", "text-purple-400")
        ]

    # A. Inicialización
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