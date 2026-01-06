import dash
from dash import html, dcc, Input, Output, State, ctx, no_update
from config import logger
from game_logic import initialize_game, process_turn

# --- CONFIGURACION DE DESARROLLO ---
# Pon esto en False cuando quieras jugar con la IA real.
# Ponlo en True para probar la interfaz rapidamente sin IA (Mock).
DEV_MODE = False 

# Inicializar la app
app = dash.Dash(__name__, update_title=None)
app.title = "RPG Adventure - Local AI"

# --- LAYOUT (DISEÑO VISUAL) ---
app.layout = html.Div([
    # 1. Cabecera y Estado
    html.Div([
        html.H1("🐉 Dungeon Master AI", style={'marginBottom': '10px'}),
        html.Div(id="stats-bar", className="stats-container", style={
            'padding': '15px', 
            'backgroundColor': '#2c3e50', 
            'color': 'white', 
            'borderRadius': '8px',
            'fontFamily': 'monospace',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        })
    ], style={'textAlign': 'center', 'marginBottom': '20px', 'maxWidth': '800px', 'margin': '20px auto'}),

    # 2. Área de Chat (Estático)
    html.Div([
        dcc.Textarea(
            id="chat-display",
            readOnly=True,
            style={
                'width': '100%', 
                'height': '500px', 
                'resize': 'none', 
                'padding': '15px', 
                'fontSize': '16px',
                'lineHeight': '1.5',
                'border': '1px solid #ccc',
                'borderRadius': '5px',
                'backgroundColor': '#f9f9f9',
                'fontFamily': 'Segoe UI, sans-serif'
            }
        )
    ], style={'maxWidth': '800px', 'margin': '0 auto'}),

    # 3. Controles de Usuario
    html.Div([
        dcc.Input(
            id="user-input", 
            type="text", 
            placeholder="¿Qué quieres hacer? (Ej: Atacar, Buscar, Huir)", 
            autoFocus=True, 
            debounce=True, # Espera a Enter o clic fuera
            style={'width': '75%', 'padding': '12px', 'fontSize': '16px', 'borderRadius': '4px', 'border': '1px solid #ccc'}
        ),
        html.Button(
            "Enviar Acción", 
            id="send-btn", 
            n_clicks=0, 
            style={
                'width': '20%', 
                'marginLeft': '4%', 
                'padding': '12px', 
                'backgroundColor': '#e74c3c', 
                'color': 'white', 
                'border': 'none', 
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontSize': '16px'
            }
        ),
    ], style={'maxWidth': '800px', 'margin': '20px auto', 'display': 'flex'}),

    # 4. INDICADOR DE CARGA (SPINNER)
    # Aquí es donde ocurre la magia visual. Se activa cuando el callback actualiza 'loading-trigger'.
    html.Div([
        dcc.Loading(
            id="loading-spinner",
            type="dot", # Opciones: "dot", "circle", "default"
            color="#2c3e50",
            children=html.Div(id="loading-trigger") # Div vacío objetivo
        )
    ], style={'height': '50px', 'textAlign': 'center'}),

    # 5. Botones de Sistema
    html.Div([
        html.Button("🔄 Nueva Partida", id="reset-btn", n_clicks=0, style={'padding': '8px 16px', 'cursor': 'pointer'}),
        html.Div(id="dev-mode-indicator", style={'marginTop': '10px', 'color': 'gray', 'fontSize': '12px'})
    ], style={'textAlign': 'center', 'marginTop': '10px'}),

    # 6. ALMACENAMIENTO DE ESTADO
    dcc.Store(id='game-store', storage_type='session'), 
])

# --- CALLBACKS (CEREBRO DE INTERACCION) ---
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
    dev_msg = f"🛠️ MOCK MODE: {'ACTIVADO' if DEV_MODE else 'DESACTIVADO'}"
    
    # A. Inicialización (Carga inicial o Botón Reset)
    if not current_state or trigger == "reset-btn":
        logger.info("Iniciando nueva partida...")
        new_state = initialize_game()
        
        # Formatear barra de estado
        inv_str = ", ".join(new_state['inventory'])
        stats_html = [
            html.Span(f"📍 {new_state['location']} ", style={'marginRight': '15px'}),
            html.Span(f"❤️ {new_state['health']} HP ", style={'color': '#e74c3c', 'marginRight': '15px', 'fontWeight': 'bold'}),
            html.Span(f"💰 {new_state['gold']} Oro ", style={'color': '#f1c40f', 'marginRight': '15px'}),
            html.Span(f"🎒 {inv_str}")
        ]
        
        return new_state['display_log'], stats_html, "", new_state, dev_msg, ""

    # B. Turno del Jugador
    if (trigger == "send-btn" or trigger == "user-input") and user_text:
        
        # LLAMADA A TU LÓGICA (game_logic.py)
        new_state, turn_text = process_turn(user_text, current_state, mock=DEV_MODE)
        
        # Actualizamos el log visual completo
        full_log = (current_chat_text or "") + turn_text
        new_state['display_log'] = full_log 

        # Actualizar Stats Visuales
        inv_str = ", ".join(new_state['inventory'])
        stats_html = [
            html.Span(f"📍 {new_state.get('location', '???')} ", style={'marginRight': '15px'}),
            html.Span(f"❤️ {new_state['health']} HP ", style={'color': '#e74c3c' if new_state['health'] < 30 else 'white', 'marginRight': '15px', 'fontWeight': 'bold'}),
            html.Span(f"💰 {new_state['gold']} Oro ", style={'color': '#f1c40f', 'marginRight': '15px'}),
            html.Span(f"🎒 {inv_str}")
        ]

        return full_log, stats_html, "", new_state, dev_msg, ""

    # C. Sin cambios
    return no_update, no_update, no_update, no_update, dev_msg, no_update

if __name__ == "__main__":
    app.run(debug=True, port=8050)