from dash import html, dcc

# --- VISUAL HELPERS ---

def render_health_bar(current_hp, max_hp=100):
    """Renderiza una barra de vida visual estilo RPG."""
    percentage = max(0, min(100, (current_hp / max_hp) * 100))
    
    # Determinar color basado en el porcentaje
    if percentage > 50:
        bar_color = "bg-green-500"
    elif percentage > 25:
        bar_color = "bg-yellow-500"
    else:
        bar_color = "bg-red-600 animate-pulse" # Parpadea si es crítico

    return html.Div([
        # Etiqueta y Valor
        html.Div([
            html.Span("❤️ SALUD", className="text-xs font-bold text-gray-400 tracking-wider"),
            html.Span(f"{current_hp}/{max_hp}", className="text-xs font-mono text-white")
        ], className="flex justify-between mb-1"),
        
        # Fondo de la barra
        html.Div([
            # Barra de progreso
            html.Div(
                style={'width': f'{percentage}%'}, 
                className=f"h-full rounded-full transition-all duration-500 ease-out {bar_color}"
            )
        ], className="w-full bg-gray-800 rounded-full h-2.5 border border-gray-700")
    ], className="w-full") # Ocupa todo el ancho disponible en su tarjeta

def render_stat_card_simple(icon, label, value, color_class="text-white"):
    """Tarjeta simple para Oro, Ubicación, etc."""
    return html.Div([
        html.Span(icon, className="text-2xl mr-3"),
        html.Div([
            html.Div(label, className="text-[10px] text-gray-500 uppercase tracking-widest font-bold"),
            html.Div(value, className=f"text-lg font-bold {color_class}")
        ], className="flex flex-col")
    ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800")

# --- MAIN AREAS ---

def render_chat_area():
    """
    Área de texto principal. 
    Usamos dcc.Markdown en lugar de Textarea para tener negritas y estilos.
    El ID 'chat-scroll-box' es importante para el auto-scroll.
    """
    return html.Div([
        html.Div(
            id="chat-scroll-box", # ID objetivo para el JavaScript de scroll
            className="w-full h-[500px] bg-gray-950/80 border border-gray-800 rounded-lg p-6 overflow-y-auto shadow-inner custom-scrollbar",
            children=[
                dcc.Markdown(
                    id="chat-display",
                    className="prose prose-invert max-w-none text-gray-300 font-mono text-sm leading-relaxed"
                )
            ]
        )
    ], className="mb-4 relative")

def render_input_area():
    """Input de texto y botón de acción."""
    return html.Div([
        dcc.Input(
            id="user-input", 
            type="text", 
            placeholder="Describe tu acción...", 
            autoFocus=True, 
            debounce=True,
            className="flex-grow bg-gray-800 text-white border border-gray-700 rounded-l-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 transition-all placeholder-gray-500"
        ),
        html.Button(
            "ACTUAR", 
            id="send-btn", 
            n_clicks=0, 
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-r-lg transition-colors duration-200 uppercase tracking-wide shadow-lg"
        ),
    ], className="flex w-full mb-2 shadow-lg")

def render_loading_spinner():
    return html.Div([
        dcc.Loading(
            id="loading-spinner",
            type="dot",
            color="#ef4444", 
            children=html.Div(id="loading-trigger")
        )
    ], className="h-8 flex justify-center items-center mb-8")

def render_footer():
    """Botones de sistema con mejor estilo."""
    btn_base = "px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all border flex items-center gap-2"
    
    return html.Div([
        html.Div([
            html.Button("💾 Guardar", id="save-btn", className=f"{btn_base} bg-blue-900/20 text-blue-400 border-blue-900 hover:bg-blue-900/50"),
            html.Button("📂 Cargar", id="load-btn", className=f"{btn_base} bg-emerald-900/20 text-emerald-400 border-emerald-900 hover:bg-emerald-900/50"),
            html.Button("💀 Reiniciar", id="reset-btn", className=f"{btn_base} bg-red-900/20 text-red-400 border-red-900 hover:bg-red-900/50"),
        ], className="flex justify-center gap-3 mb-4"),
        
        html.Div(id="dev-mode-indicator", className="text-gray-700 text-[10px] font-mono")
    ], className="text-center pb-8")