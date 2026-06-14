import unittest

from services.qa_service import answer_question


class QAServiceTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "classification": [
                {"team": "Spain", "group": "H", "points": 6, "goal_difference": 4, "played": 2},
                {"team": "Brazil", "group": "C", "points": 4, "goal_difference": 1, "played": 2},
            ],
            "top_scorers": [{"player": "Mbappé", "team": "France", "goals": 5}],
            "advanced_player_stats": {
                "rankings": {
                    "youngest": [{"player": "Jugador Joven", "team": "Spain", "date_of_birth": "2007-07-13", "age": 18}],
                    "yellow_cards": [{"player": "Jugador A", "team": "Mexico", "yellow_cards": 3}],
                    "saves": [{"player": "Portero A", "team": "Spain", "saves": 11}],
                },
                "metadata": {"source": "balldontlie", "players_count": 3},
            },
            "matches": [
                {"home_team_name_en": "Spain", "away_team_name_en": "Japan", "local_date": "2026-06-18 18:00", "stadium": "Estadio Azteca", "finished": False, "time_elapsed": "notstarted"},
                {"home_team_name_en": "Brazil", "away_team_name_en": "Argentina", "local_date": "2026-06-17 20:00", "stadium": "Estadio MetLife", "finished": True, "home_score": 2, "away_score": 1, "time_elapsed": "finished"},
            ],
        }

    def test_leader_question(self):
        result = answer_question("¿Quién lidera el grupo H?", self.data)
        self.assertIn("Spain", result["answer"])
        self.assertEqual(result["source"], "rules")

    def test_points_question_with_alias(self):
        result = answer_question("¿Cuántos puntos tiene mexico?", self.data)
        self.assertIn("No tengo", result["answer"]) or "Mexico" in result["answer"]

    def test_prediction_question(self):
        result = answer_question("¿Quién ganará España vs Brasil?", self.data)
        self.assertIn("España", result["answer"]) or "Brasil" in result["answer"]

    def test_youngest_player_question_uses_advanced_stats(self):
        result = answer_question("¿Quién es el jugador más joven del Mundial?", self.data)
        self.assertIn("Jugador Joven", result["answer"])
        self.assertEqual(result["source"], "balldontlie")

    def test_yellow_cards_question_uses_advanced_stats(self):
        result = answer_question("¿Quién tiene más tarjetas amarillas?", self.data)
        self.assertIn("Jugador A", result["answer"])
        self.assertIn("amarillas", result["answer"])

    def test_goalkeeper_saves_question_uses_advanced_stats(self):
        result = answer_question("¿Qué portero tiene más paradas?", self.data)
        self.assertIn("Portero A", result["answer"])
        self.assertIn("paradas", result["answer"])

    def test_offsides_question_has_clear_limitation(self):
        result = answer_question("¿Qué jugador tiene más fueras de juego?", self.data)
        self.assertIn("equipo", result["answer"])

    def test_intent_detection_for_support_message(self):
        result = answer_question("¿Qué puedo preguntarte?", self.data)
        answer = result["answer"].lower()
        self.assertTrue("puedes preguntarme" in answer or "clasificación" in answer)


if __name__ == "__main__":
    unittest.main()
