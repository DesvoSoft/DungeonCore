from dash import html, dcc
from frontend.components import (
    render_chat_area, 
    render_input_area, 
    render_loading_spinner, 
    render_footer
)

def build_layout():
    """Construye el layout principal de la aplicación."""
    return html.Div([
        
        # Contenedor Principal
        html.Div([
            
            # HEADER
            html.H1("🐉 DungeonCore", className="text-4xl md:text-5xl font-bold text-center text-red-500 mb-6 mt-8 tracking-wider drop-shadow-lg"),

            # BARRA DE ESTADO (Vacía al inicio, se llena via callback)
            html.Div(
                id="stats-bar", 
                className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 bg-gray-900 p-4 rounded-xl border border-gray-800 shadow-xl"
            ),

            # COMPONENTES
            render_chat_area(),
            render_input_area(),
            render_loading_spinner(),
            render_footer()

        ], className="max-w-4xl mx-auto px-4 min-h-screen flex flex-col justify-center"),
        
        # TIENDAS DE DATOS (Invisibles)
        dcc.Store(id='game-store', storage_type='session') 

    ], className="bg-gray-950 min-h-screen text-gray-100 selection:bg-red-900 selection:text-white")