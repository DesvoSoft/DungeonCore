import unittest
from game_logic import process_turn, initialize_game

class TestGameLogic(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test: Prepara un estado limpio"""
        self.state = initialize_game()

    def test_initialization(self):
        """Prueba que el juego inicie con 100 de vida"""
        self.assertEqual(self.state['health'], 100)
        self.assertIn("Antorcha", self.state['inventory'])

    def test_damage_processing(self):
        """Prueba si recibimos daño correctamente (Usando MOCK)"""
        # Simulamos un turno con Mock=True (sabemos que el mock quita 5 de vida)
        new_state, text = process_turn("Atacar", self.state, mock=True)
        
        # El mock en ai_engine.py estaba definido para quitar 5 HP
        # Verifica ai_engine.py si cambiaste los valores del mock
        expected_hp = 95 
        
        self.assertEqual(new_state['health'], expected_hp)
        self.assertIn("-5 HP", text) # Verifica que el texto muestre el daño

    def test_death_logic(self):
        """Prueba qué pasa si la vida llega a 0"""
        self.state['health'] = 5
        # El mock quita 5, así que deberíamos llegar a 0
        new_state, text = process_turn("Atacar suicida", self.state, mock=True)
        
        self.assertEqual(new_state['health'], 0)
        self.assertIn("HAS MUERTO", text)

    def test_inventory_update(self):
        """Prueba recibir un ítem"""
        # El mock da una "Roca de Testeo"
        new_state, _ = process_turn("Buscar", self.state, mock=True)
        self.assertIn("Roca de Testeo", new_state['inventory'])

if __name__ == '__main__':
    unittest.main()