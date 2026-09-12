"""Application settings for the local NLP chatbot."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CHATBOT_NAME = "NLP Learning Chatbot"
AUTHOR = "yuzaki_x_nasa"
VERSION = "2.0.0"
MIN_CONFIDENCE = 0.20
HISTORY_LENGTH = 10
KNOWLEDGE_FILE = PROJECT_ROOT / "data" / "knowledge.txt"
RESPONSES_FILE = PROJECT_ROOT / "data" / "responses.json"
