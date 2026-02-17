import dash
from dash import html, dcc, Input, Output, State, ctx, no_update, clientside_callback
from config import logger
from game_logic import initialize_game, process_turn, save_game_state, load_game_state, get_save_info
from game_logic import get_next_level_xp, MAX_LEVEL, MAX_INVENTORY
from frontend.layout import build_layout
from frontend.components import render_stat_card_simple, render_health_bar, render_xp_bar, render_combat_card

DEV_MODE = False

external_scripts = [
    {'src': 'https://cdn.tailwindcss.com?plugins=typography'} 
]

app = dash.Dash(__name__, 
                external_scripts=external_scripts,
                update_title=None)

app.title = "DungeonCore AI"
app.layout = build_layout()

def render_stats_panel(state):
    level = state.get("level", 1)
    xp = state.get("xp", 0)
    next_xp = get_next_level_xp(level)
    health = state.get("health", 0)
    max_health = state.get("max_health", 100)
    gold = state.get("gold", 0)
    location = state.get("location", "Unknown")
    inventory = state.get("inventory", [])
    equipment = state.get("equipment", {})
    combat = state.get("combat", {})
    
    inv_count = len(inventory)
    
    cards = [
        html.Div([
            html.Div([
                html.Span("🗡️", className="text-xl mr-2"),
                html.Div([
                    html.Span("NIVEL", className="text-[10px] text-gray-500 uppercase tracking-widest font-bold"),
                    html.Span(f"{level}", className="text-lg font-bold text-orange-400")
                ], className="flex flex-col")
            ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800")
        ], className="col-span-1"),
        
        html.Div([
            render_xp_bar(xp, next_xp, level)
        ], className="col-span-1"),
        
        render_stat_card_simple("📍", "Ubicación", location[:20] + "..." if len(location) > 20 else location, "text-blue-400"),
        
        html.Div([
            render_health_bar(health, max_health)
        ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800 col-span-1"),
        
        render_stat_card_simple("💰", "Oro", str(gold), "text-yellow-400"),
        
        html.Div([
            html.Span("🎒", className="text-xl mr-3"),
            html.Div([
                html.Span("MOCHILA", className="text-[10px] text-gray-500 uppercase tracking-widest font-bold"),
                html.Span(f"{inv_count}/{MAX_INVENTORY}", className="text-lg font-bold text-purple-400")
            ], className="flex flex-col")
        ], className="flex items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800")
    ]
    
    if combat.get("active"):
        cards.append(html.Div([
            render_combat_card(combat)
        ], className="col-span-2 md:col-span-3"))
    
    return cards

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

@app.callback(
    [Output("chat-display", "children"),
     Output("stats-bar", "children"),
     Output("user-input", "value"),
     Output("game-store", "data"),
     Output("dev-mode-indicator", "children"),
     Output("loading-trigger", "children"),
     Output("save-slot-display", "children")], 
    [Input("send-btn", "n_clicks"),
     Input("user-input", "n_submit"),
     Input("reset-btn", "n_clicks"),
     Input("save-slot-1", "n_clicks"),
     Input("save-slot-2", "n_clicks"),
     Input("save-slot-3", "n_clicks"),
     Input("load-slot-1", "n_clicks"),
     Input("load-slot-2", "n_clicks"),
     Input("load-slot-3", "n_clicks")],
    [State("user-input", "value"),
     State("game-store", "data"),
     State("chat-display", "children")]
)
def main_game_loop(btn_click, enter_submit, reset_click, 
                   save1, save2, save3, load1, load2, load3,
                   user_text, current_state, current_chat_children):
    trigger = ctx.triggered_id
    dev_msg = f"🛠️ MOCK: {'ON' if DEV_MODE else 'OFF'}"
    
    current_log_text = current_chat_children if isinstance(current_chat_children, str) else ""
    if not current_log_text: 
        current_log_text = ""
    
    slot_display = ""
    for slot in [1, 2, 3]:
        info = get_save_info(slot)
        if info:
            status = "☠️" if info.get("game_over") else "✅"
            slot_display += f"| Ranura {slot}: {status} Nivel {info['level']} | "
    
    if not current_state or trigger == "reset-btn":
        logger.info("Iniciando nueva partida...")
        new_state = initialize_game()
        return new_state['display_log'], render_stats_panel(new_state), "", new_state, dev_msg, "", slot_display
    
    if trigger == "save-slot-1":
        success, msg = save_game_state(current_state, 1)
        updated_log = current_log_text + f"\n\n💾 **{msg}**"
        current_state['display_log'] = updated_log
        return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if trigger == "save-slot-2":
        success, msg = save_game_state(current_state, 2)
        updated_log = current_log_text + f"\n\n💾 **{msg}**"
        current_state['display_log'] = updated_log
        return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if trigger == "save-slot-3":
        success, msg = save_game_state(current_state, 3)
        updated_log = current_log_text + f"\n\n💾 **{msg}**"
        current_state['display_log'] = updated_log
        return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if trigger == "load-slot-1":
        loaded_state, msg = load_game_state(1)
        if loaded_state:
            return loaded_state['display_log'], render_stats_panel(loaded_state), "", loaded_state, dev_msg, "", slot_display
        else:
            updated_log = current_log_text + f"\n\n⚠️ **{msg}**"
            return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if trigger == "load-slot-2":
        loaded_state, msg = load_game_state(2)
        if loaded_state:
            return loaded_state['display_log'], render_stats_panel(loaded_state), "", loaded_state, dev_msg, "", slot_display
        else:
            updated_log = current_log_text + f"\n\n⚠️ **{msg}**"
            return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if trigger == "load-slot-3":
        loaded_state, msg = load_game_state(3)
        if loaded_state:
            return loaded_state['display_log'], render_stats_panel(loaded_state), "", loaded_state, dev_msg, "", slot_display
        else:
            updated_log = current_log_text + f"\n\n⚠️ **{msg}**"
            return updated_log, render_stats_panel(current_state), "", current_state, dev_msg, "", slot_display
    
    if (trigger == "send-btn" or trigger == "user-input") and user_text:
        new_state, turn_text = process_turn(user_text, current_state, mock=DEV_MODE)
        
        turn_text_md = turn_text.replace("👤 TÚ:", "\n> **👤 TÚ:**").replace("🎲 DM:", "\n**🎲 DM:**")
        
        full_log = current_log_text + turn_text_md
        new_state['display_log'] = full_log 
        
        return full_log, render_stats_panel(new_state), "", new_state, dev_msg, "", slot_display
    
    return no_update, no_update, no_update, no_update, dev_msg, no_update, slot_display

if __name__ == "__main__":
    app.run(debug=True, port=8050)
