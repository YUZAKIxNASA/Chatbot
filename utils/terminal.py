"""Lightweight terminal interface."""

import os
from typing import Optional

from chatbot.engine import ChatbotEngine
from config import AUTHOR, CHATBOT_NAME, VERSION
from utils.logger import get_logger


HELP_TEXT = "Commands: help, clear, history, reset, status, exit (or bye)."


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_history(engine: ChatbotEngine) -> None:
    entries = engine.recent_history()
    if not entries:
        print("Bot: No conversation history yet.")
        return
    for user, bot in entries:
        print(f"You: {user}\nBot: {bot}")


def run_chatbot(engine: Optional[ChatbotEngine] = None) -> None:
    logger = get_logger()
    try:
        engine = engine or ChatbotEngine()
    except (OSError, ValueError) as error:
        logger.error("Unable to start chatbot: %s", error)
        print("Bot: I could not load my local knowledge base.")
        return
    clear_screen()
    print("=" * 70)
    print(f"{CHATBOT_NAME} v{VERSION} by {AUTHOR}")
    print("Ask a question, or type 'help' for commands.")
    print("=" * 70)
    logger.info("Chatbot started")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye, take care!")
            break
        command = user_input.lower()
        if command in {"exit", "bye", "quit"}:
            print(f"Bot: {engine.respond(user_input)}")
            break
        if command == "help":
            print(f"Bot: {HELP_TEXT}")
        elif command == "clear":
            clear_screen()
        elif command == "history":
            print_history(engine)
        elif command == "reset":
            engine.clear_history()
            print("Bot: Conversation history cleared.")
        elif command == "status":
            print(f"Bot: {engine.status()}")
        else:
            print(f"Bot: {engine.respond(user_input)}")
