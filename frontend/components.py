from dash import html, dcc

def render_health_bar(current_hp, max_hp=100):
    percentage = max(0, min(100, (current_hp / max_hp) * 100))
    
    if percentage > 50:
        bar_color = "bg-green-500"
    elif percentage > 25:
        bar_color = "bg-yellow-500"
    else:
        bar_color = "bg-red-600 animate-pulse"
    
    return html.Div([
        html.Div([
            html.Span("❤️ SALUD", className="text-xs font-bold text-gray-400 tracking-wider"),
            html.Span(f"{current_hp}/{max_hp}", className="text-xs font-mono text-white")
        ], className="flex justify-between mb-1"),
        
        html.Div([
            html.Div(
                style={'width': f'{percentage}%'}, 
                className=f"h-full rounded-full transition-all duration-500 ease-out {bar_color}"
            )
        ], className="w-full bg-gray-800 rounded-full h-2.5 border border-gray-700")
    ], className="w-full")

def render_xp_bar(current_xp, next_xp, level):
    if next_xp is None:
        xp_percent = 100
        xp_text = "MAX"
    else:
        xp_percent = max(0, min(100, (current_xp / next_xp) * 100))
        xp_text = f"{current_xp}/{next_xp}"
    
    return html.Div([
        html.Div([
            html.Span("⭐ EXPERIENCIA", className="text-xs font-bold text-gray-400 tracking-wider"),
            html.Span(xp_text, className="text-xs font-mono text-white")
        ], className="flex justify-between mb-1"),
        
        html.Div([
            html.Div(
                style={'width': f'{xp_percent}%'}, 
                className="h-full rounded-full transition-all duration-500 ease-out bg-orange-500"
            )
        ], className="w-full bg-gray-800 rounded-full h-2.5 border border-gray-700")
    ], className="w-full")

def render_combat_card(combat):
    enemy_name = combat.get("enemy_name", "Unknown")
    enemy_hp = combat.get("enemy_hp", 0)
    enemy_max_hp = combat.get("enemy_max_hp", 1)
    last_roll = combat.get("last_roll")
    enemy_damage = combat.get("enemy_damage")
    
    hp_percent = max(0, min(100, (enemy_hp / enemy_max_hp) * 100))
    
    info_parts = [f"⚔️ {enemy_name}"]
    if last_roll:
        info_parts.append(f"Dado: {last_roll}")
    if enemy_damage:
        info_parts.append(f"Daño recibido: {enemy_damage}")
    
    return html.Div([
        html.Div([
            html.Span("⚔️ COMBATE", className="text-xs font-bold text-red-400 tracking-wider"),
        ], className="flex justify-between mb-2"),
        
        html.Div([
            html.Div(
                style={'width': f'{hp_percent}%'}, 
                className="h-full rounded-full transition-all duration-300 bg-red-600"
            )
        ], className="w-full bg-gray-800 rounded-full h-3 border border-red-900 mb-2"),
        
        html.Div([
            html.Span(f"{enemy_name} - HP: {enemy_hp}/{enemy_max_hp}", className="text-sm text-red-300 font-mono")
        ]),
        
        html.Div([
            html.Span(" | ".join(info_parts), className="text-xs text-gray-500")
        ])
    ], className="bg-red-950/30 p-3 rounded-lg border border-red-800")

def render_stat_card_simple(icon, label, value, color_class="text-white"):
    return html.Div([
        html.Span(icon, className="text-2xl mr-3"),
        html.Div([
            html.Div(label, className="text-[10px] text-gray-500 uppercase tracking-widest font-bold"),
            html.Div(value, className=f"text-lg font-bold {color_class}")
        ], className="flex flex-col")
    ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800")

def render_chat_area():
    return html.Div([
        html.Div(
            id="chat-scroll-box",
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
    btn_base = "px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all border flex items-center gap-2"
    
    return html.Div([
        html.Div([
            html.Div([
                html.Button("💾 S1", id="save-slot-1", className=f"{btn_base} bg-blue-900/20 text-blue-400 border-blue-900 hover:bg-blue-900/50"),
                html.Button("📂 S1", id="load-slot-1", className=f"{btn_base} bg-emerald-900/20 text-emerald-400 border-emerald-900 hover:bg-emerald-900/50"),
            ], className="flex gap-2"),
            
            html.Div([
                html.Button("💾 S2", id="save-slot-2", className=f"{btn_base} bg-blue-900/20 text-blue-400 border-blue-900 hover:bg-blue-900/50"),
                html.Button("📂 S2", id="load-slot-2", className=f"{btn_base} bg-emerald-900/20 text-emerald-400 border-emerald-900 hover:bg-emerald-900/50"),
            ], className="flex gap-2"),
            
            html.Div([
                html.Button("💾 S3", id="save-slot-3", className=f"{btn_base} bg-blue-900/20 text-blue-400 border-blue-900 hover:bg-blue-900/50"),
                html.Button("📂 S3", id="load-slot-3", className=f"{btn_base} bg-emerald-900/20 text-emerald-400 border-emerald-900 hover:bg-emerald-900/50"),
            ], className="flex gap-2"),
            
            html.Button("💀 Reiniciar", id="reset-btn", className=f"{btn_base} bg-red-900/20 text-red-400 border-red-900 hover:bg-red-900/50"),
        ], className="flex flex-wrap justify-center gap-3 mb-4"),
        
        html.Div(id="save-slot-display", className="text-gray-600 text-[10px] font-mono text-center mb-2"),
        
        html.Div(id="dev-mode-indicator", className="text-gray-700 text-[10px] font-mono text-center")
    ], className="text-center pb-8")
