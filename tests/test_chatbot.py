import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from chatbot.engine import ChatbotEngine
from chatbot.greetings import is_farewell, is_greeting
from chatbot.nlp import normalize_text
from utils.terminal import run_chatbot


class ChatbotTests(unittest.TestCase):
    def setUp(self):
        self.engine = ChatbotEngine()

    def test_normalization(self):
        self.assertEqual(normalize_text(" Hello, NLP! "), "hello nlp")

    def test_greeting_detection_does_not_match_questions(self):
        self.assertTrue(is_greeting("Good morning"))
        self.assertFalse(is_greeting("Can you explain Python?"))

    def test_farewell_detection(self):
        self.assertTrue(is_farewell("see you"))
        self.assertFalse(is_farewell("tell me about Git"))

    def test_empty_input(self):
        self.assertIn("Please enter", self.engine.respond(""))
        self.assertEqual(len(self.engine.recent_history()), 0)

    def test_known_question(self):
        response = self.engine.respond("What is Python?")
        self.assertIn("programming language", response)
        self.assertEqual(self.engine.status()["matched"], 1)

    def test_unknown_question_uses_confidence_threshold(self):
        response = self.engine.respond("xyzzy completely unknown topic")
        self.assertIn(response, self.engine.responses.data["fallback"])
        self.assertEqual(self.engine.status()["fallbacks"], 1)

    def test_threshold_can_reject_a_weak_match(self):
        strict_engine = ChatbotEngine(min_confidence=1.01)
        strict_engine.respond("Python")
        self.assertEqual(strict_engine.status()["fallbacks"], 1)

    def test_response_and_history(self):
        self.assertIn("Hello", self.engine.respond("hi"))
        self.assertIn("welcome", self.engine.respond("thanks").lower())
        self.assertEqual(len(self.engine.recent_history()), 2)

    def test_reset_clears_history(self):
        self.engine.respond("hello")
        self.engine.clear_history()
        self.assertEqual(self.engine.recent_history(), [])

    def test_terminal_commands(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["help", "history", "reset", "clear", "exit"]), \
                patch("utils.terminal.clear_screen"), redirect_stdout(output):
            run_chatbot(self.engine)
        text = output.getvalue()
        self.assertIn("Commands:", text)
        self.assertIn("Conversation history cleared", text)
        self.assertIn("Goodbye", text)


if __name__ == "__main__":
    unittest.main()
