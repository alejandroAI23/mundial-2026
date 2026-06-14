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
            "matches": [
                {
                    "home_team_name_en": "Spain",
                    "away_team_name_en": "Japan",
                    "local_date": "2026-06-18 18:00",
                    "stadium": "Estadio Azteca",
                    "finished": False,
                    "time_elapsed": "notstarted",
                },
                {
                    "home_team_name_en": "Brazil",
                    "away_team_name_en": "Argentina",
                    "local_date": "2026-06-17 20:00",
                    "stadium": "Estadio MetLife",
                    "finished": True,
                    "home_score": 2,
                    "away_score": 1,
                    "time_elapsed": "finished",
                },
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


if __name__ == "__main__":
    unittest.main()
