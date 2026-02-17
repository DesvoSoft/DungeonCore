from dash import html, dcc
from frontend.components import (
    render_chat_area, 
    render_input_area, 
    render_loading_spinner, 
    render_footer
)

def build_layout():
    return html.Div([
        html.Div([
            html.H1("🐉 DungeonCore", className="text-4xl md:text-5xl font-bold text-center text-red-500 mb-6 mt-8 tracking-wider drop-shadow-lg"),
            
            html.Div(
                id="stats-bar", 
                className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 bg-gray-900 p-4 rounded-xl border border-gray-800 shadow-xl"
            ),
            
            render_chat_area(),
            render_input_area(),
            render_loading_spinner(),
            render_footer()
            
        ], className="max-w-4xl mx-auto px-4 min-h-screen flex flex-col justify-center"),
        
        dcc.Store(id='game-store', storage_type='session'),
        
    ], className="bg-gray-950 min-h-screen text-gray-100 selection:bg-red-900 selection:text-white")
