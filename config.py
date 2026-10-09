"""Application settings for the local NLP chatbot."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CHATBOT_NAME = "NLP Learning Chatbot"
AUTHOR = "yuzaki_x_nasa"
VERSION = "2.0.0"
MIN_CONFIDENCE = 0.20
HISTORY_LENGTH = 10
KNOWLEDGE_FILE = PROJECT_ROOT / "data" / "knowledge.txt"
KNOWLEDGE_STORE_FILE = PROJECT_ROOT / "data" / "knowledge.json"
RESPONSES_FILE = PROJECT_ROOT / "data" / "responses.json"
MODEL_NAME = "tfidf"
TFIDF_ENABLED = True
SAVE_CONVERSATION_HISTORY = False
CONVERSATION_HISTORY_FILE = PROJECT_ROOT / "data" / "conversations" / "history.json"
DEBUG_LOGGING = False
ENABLED_ACTIONS = {"knowledge": True, "calculator": True}
