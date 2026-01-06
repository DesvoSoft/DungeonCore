import unittest
from ai_engine import clean_json_response, query_dm

class TestAIEngine(unittest.TestCase):

    def test_json_cleaner_simple(self):
        """Prueba si limpia un JSON limpio"""
        raw = '{"key": "value"}'
        self.assertEqual(clean_json_response(raw), raw)

    def test_json_cleaner_dirty(self):
        """Prueba si elimina texto basura (Markdown)"""
        raw = 'Claro, aquí tienes el JSON:\n```json\n{"hp": 10}\n```\nEspero te sirva.'
        expected = '{"hp": 10}'
        self.assertEqual(clean_json_response(raw), expected)

    def test_mock_mode(self):
        """Prueba que el modo Mock devuelve la estructura correcta"""
        state = {"hp": 100}
        response = query_dm("Atacar", state, mock=True)
        
        self.assertIn("narrative", response)
        self.assertIsInstance(response["hp_change"], int)
        self.assertEqual(response["new_item"], "Roca de Testeo")

if __name__ == '__main__':
    unittest.main()