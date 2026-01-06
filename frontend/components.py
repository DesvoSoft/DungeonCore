from dash import html, dcc

# --- ATOMS (Pequeñas piezas UI) ---

def render_stat_card(icon, label, value, color_class="text-white"):
    """Renderiza una tarjeta de estadística individual."""
    return html.Div([
        html.Span(icon, className="text-2xl mr-2"),
        html.Div([
            html.Div(label, className="text-xs text-gray-500 uppercase tracking-wider font-bold"),
            html.Div(value, className=f"text-lg font-bold {color_class}")
        ], className="flex flex-col")
    ], className="flex items-center justify-center bg-gray-800/50 p-2 rounded-lg border border-gray-700/50 hover:border-gray-600 transition-colors")

def render_chat_area():
    """El área de texto principal."""
    return html.Div([
        dcc.Textarea(
            id="chat-display",
            readOnly=True,
            className="w-full h-[500px] bg-gray-950 text-gray-300 border border-gray-800 rounded-lg p-4 font-mono text-base focus:outline-none focus:border-red-500 transition-colors resize-none shadow-inner scrollbar-thin",
            style={'fontFamily': '"Fira Code", monospace'} 
        )
    ], className="mb-4 relative")

def render_input_area():
    """Input de texto y botón de acción."""
    return html.Div([
        dcc.Input(
            id="user-input", 
            type="text", 
            placeholder="¿Qué haces? (Ej: Atacar, Huir, Inventario...)", 
            autoFocus=True, 
            debounce=True,
            className="flex-grow bg-gray-800 text-white border border-gray-700 rounded-l-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all placeholder-gray-500"
        ),
        html.Button(
            "ACTUAR", 
            id="send-btn", 
            n_clicks=0, 
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-r-lg transition-colors duration-200 uppercase tracking-wide shadow-lg hover:shadow-red-900/20"
        ),
    ], className="flex w-full mb-2 shadow-lg")

def render_loading_spinner():
    """Spinner de carga."""
    return html.Div([
        dcc.Loading(
            id="loading-spinner",
            type="dot",
            color="#ef4444", 
            children=html.Div(id="loading-trigger")
        )
    ], className="h-8 flex justify-center items-center mb-8")

def render_footer():
    """Botones de sistema y footer."""
    return html.Div([
        html.Button(
            "🔄 Reiniciar Partida", 
            id="reset-btn", 
            n_clicks=0, 
            className="text-gray-500 hover:text-white text-sm border border-gray-700 hover:border-gray-500 px-4 py-2 rounded-full transition-all"
        ),
        html.Div(id="dev-mode-indicator", className="text-gray-600 text-xs mt-3 font-mono")
    ], className="text-center pb-8")