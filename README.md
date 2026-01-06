# DungeonCore: Local AI RPG Adventure (WIP)

**DungeonCore** is a text-based Role Playing Game (RPG) engine where the Dungeon Master is an autonomous Local Large Language Model (LLM) running entirely on the user's machine.

Built with **Python** and **Plotly Dash**, this project demonstrates a decoupled architecture where the game logic is separated from narrative generation. It enforces structured JSON outputs from the LLM to programmatically manage game state (Health, Gold, Inventory) while allowing for free-flowing storytelling.

## Project Overview

The core innovation of DungeonCore is the **AI Engine** (`ai_engine.py`) which forces the LLM to act as a logic processor as well as a storyteller. Instead of returning raw text, the AI returns a JSON object containing:

1. **Narrative:** The descriptive text of the adventure.
2. **State Deltas:** Numerical changes to HP, Gold, or Inventory additions.
3. **Choices:** Suggested next actions for the player.

This ensures the game state is tracked mathematically by Python, preventing the AI from "hallucinating" the player's health or inventory status.

## Prerequisites

- **Python 3.8+**
- **LM Studio**: Required to host the local model API.
- **Hardware**: A machine capable of running a quantized LLM (8GB+ RAM recommended).

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/dungeon-core.git
cd dungeon-core

```

2. **Create a virtual environment**

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

```

3. **Install dependencies**

```bash
pip install -r requirements.txt

```

## Configuration

This project connects to a local API server.

1. Open **LM Studio**.
2. Navigate to the **Local Server** tab.
3. Select a model (Recommended: _Llama 3_, _Mistral Instruct_, or _Gemma_).
4. Click **Start Server**.
5. Verify the server is running at `http://localhost:1234`.

## Usage

To start the game server:

```bash
python app.py

```

Open a web browser and navigate to `http://127.0.0.1:8050/`.

**Developer Mode:**
To test the UI and game logic without the AI server running, open `app.py` and set `DEV_MODE = True`. This will use a mock response generator.

## Project Structure

- **app.py**: The entry point. Handles the Dash frontend, UI layout, and callbacks.
- **game_logic.py**: The controller. Manages state updates, death conditions, and turn processing.
- **ai_engine.py**: The AI interface. Handles API requests, JSON cleaning, and error handling.
- **config.py**: Configuration settings, system prompts, and logging setup.
- **test_logic.py**: Unit tests for verifying game mechanics and JSON parsing.

## Roadmap and Planned Features

The project is currently in the MVP (Minimum Viable Product) phase. The following features are planned for future releases.

### Phase 1: Persistence & Stability (Current Focus)

- **Save/Load System:** Implement JSON serialization to save current progress to a local file and reload it.
- **Context Window Management:** Implement a "rolling summary" system to prevent the AI from forgetting earlier events as the conversation grows.
- **Robust JSON Repair:** Integrate a more advanced library (like `json_repair`) to handle malformed AI outputs more gracefully.

### Phase 2: Game Mechanics

- **Inventory Usage:** Allow the player to "use" items (e.g., drinking a potion to restore HP) via specific UI buttons, not just text commands.
- **Dice Roll Visualization:** Display visual dice rolls for combat encounters to increase immersion.
- **Skill Check System:** Implement a D20 system where the AI requests a skill check (Strength, Charisma) and Python calculates the success/failure based on probability.

### Phase 3: Advanced Features

- **World Lore Injection (RAG):** Integrate a Vector Database (like ChromaDB) to allow the AI to reference a large PDF of lore/rules without filling the context window.
- **Image Generation:** Optional integration with local Stable Diffusion to generate an image of the current location described by the text.
- **Custom Character Creation:** A UI form at the start of the game to set initial stats and class.
