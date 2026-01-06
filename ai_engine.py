import json
import requests
import time
import json_repair # Requires: pip install json_repair
from config import LM_STUDIO_URL, SYSTEM_PROMPT, logger

def query_dm(user_input, current_state, mock=False):
    """
    Queries the AI Dungeon Master with robust error handling and automatic JSON repair.
    Includes a retry loop to handle temporary AI hallucinations or formatting errors.
    """
    logger.info(f"Player action: {user_input}")

    # --- MOCK MODE (For testing without AI) ---
    if mock:
        time.sleep(1) 
        return {
            "narrative": f"[MOCK] You acted: '{user_input}'. The system is running in DEV_MODE.",
            "hp_change": 0, 
            "gold_change": 0, 
            "new_item": None, 
            "choices": ["Continue", "Quit"]
        }

    # --- PROMPT PREPARATION ---
    # We inject strict instructions into the user prompt to force the AI to stay in character
    # and focus on the JSON output format.
    style_injection = f"""
    [Acción del Jugador]: "{user_input}"
    
    [Instrucción]: Eres el Narrador. Narra la consecuencia inmediata de esta acción en ESPAÑOL.
    Si hay combate, usa los números del sistema. Si no, sé creativo y cruel.
    OBLIGATORIO: Responde SOLAMENTE con el objeto JSON.
    """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(state=str(current_state))},
    ]
    
    # Context Memory: Add last 6 turns
    history = current_state.get("history", [])
    if history:
        messages.extend(history[-6:])
        
    messages.append({"role": "user", "content": style_injection})

    # --- RETRY LOOP (Robustness) ---
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}...")

            # 1. API Request
            response = requests.post(
                LM_STUDIO_URL, 
                json={
                    "model": "local-model", 
                    "messages": messages, 
                    "temperature": 0.7, # Slightly lower temperature for better JSON stability
                    "max_tokens": 800
                },
                timeout=45 # Generous timeout for local LLMs
            )
            response.raise_for_status()
            
            raw_content = response.json()["choices"][0]["message"]["content"]
            logger.debug(f"AI Raw Response (Attempt {attempt+1}): {raw_content}")

            # 2. JSON Repair & Parsing
            # json_repair finds the JSON object buried in text and fixes common syntax errors
            decoded_object = json_repair.loads(raw_content)
            
            # 3. Validation
            # We ensure the critical 'narrative' field exists
            if "narrative" not in decoded_object:
                raise ValueError("Parsed JSON missing 'narrative' field")

            # If we got here, success!
            return decoded_object

        except requests.exceptions.ConnectionError:
            logger.critical("Connection Error: Is LM Studio running on port 1234?")
            return {
                "narrative": "❌ **Connection Error:** Could not reach the AI server. Please check if LM Studio is running.",
                "hp_change": 0, "gold_change": 0, "new_item": None, "choices": []
            }
            
        except Exception as e:
            logger.warning(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                time.sleep(1.5) # Wait a bit before retrying
            else:
                # Fallback if all retries fail
                logger.error("All retries failed.")
                return {
                    "narrative": f"**[SYSTEM ERROR]** The Dungeon Master is confused and could not process your action.\n\n*Debug Info:* {str(e)}",
                    "hp_change": 0, 
                    "gold_change": 0, 
                    "new_item": None, 
                    "choices": ["Try again"]
                }