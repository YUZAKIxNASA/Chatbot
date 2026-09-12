# Chatbot

Chatbot is a beginner-friendly local NLP project. It uses NLTK preprocessing and scikit-learn TF-IDF vectors to match questions against a small, editable knowledge base. It does not call an API, store data remotely, or require an account.

## Features

- Greetings, farewells, thanks, and lightweight command handling
- NLTK tokenization and lemmatization with offline fallbacks
- TF-IDF and cosine-similarity knowledge matching
- Configurable confidence threshold and fallback responses
- Local session history with `history` and `reset`
- `help`, `clear`, `status`, and `exit` terminal commands
- Small unittest suite and portable launch scripts

## Technology Stack

- Python 3.9 or newer
- NLTK
- scikit-learn

## Project Structure

```text
Chatbot/
├── main.py
├── chatbot.py              # compatibility launcher
├── config.py
├── requirements.txt
├── data/
│   ├── knowledge.txt
│   └── responses.json
├── chatbot/
│   ├── engine.py
│   ├── greetings.py
│   ├── knowledge.py
│   ├── nlp.py
│   └── responses.py
├── utils/
│   ├── logger.py
│   └── terminal.py
└── tests/
    └── test_chatbot.py
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

From the repository root:

```bash
python main.py
```

On Linux/macOS, `./run.sh` checks Python and imports before starting. On Windows, run `run.bat`. The older `python chatbot.py` command remains supported.

## Commands

| Command | Action |
| --- | --- |
| `help` | Show available commands |
| `clear` | Clear the terminal |
| `history` | Display recent exchanges |
| `reset` | Clear conversation history |
| `status` | Display version and session statistics |
| `exit`, `bye`, `quit` | End the session |

## How It Works

`chatbot/nlp.py` normalizes text, tokenizes it, and lemmatizes tokens. NLTK data is used when available; missing resources fall back to regular-expression tokenization and original tokens, so importing the project does not attempt a network download.

The knowledge loader reads facts from `data/knowledge.txt`. At startup, scikit-learn builds a TF-IDF matrix for those facts. TF-IDF gives higher weight to terms that matter in a document and lower weight to common terms. A user question is transformed using the same vocabulary, then cosine similarity compares its vector with each knowledge vector. The highest score is returned only when it reaches `MIN_CONFIDENCE` in `config.py`; otherwise a configurable fallback is used.

## Extend The Chatbot

Add one beginner-friendly fact per line to `data/knowledge.txt`. Edit the fallback, thanks, empty-input, or error text in `data/responses.json`. Paths, name, version, history size, and confidence threshold are centralized in `config.py`.

## Testing

```bash
python -m unittest discover
```

The tests cover normalization, greetings, farewells, empty input, known and unknown questions, confidence thresholds, responses, history, reset, and terminal commands.

## Troubleshooting

- If imports fail, activate the virtual environment and run `python -m pip install -r requirements.txt`.
- Run commands from the repository root so the package imports and data paths resolve normally.
- NLTK resources are optional for this project. If unavailable, the local fallback keeps the chatbot usable with simpler tokenization.
- A missing knowledge file prevents startup because matching cannot work without facts. A missing or invalid response file uses built-in safe defaults.

## Limitations and Future Improvements

This is a small retrieval chatbot, not a generative assistant. It answers only from its local facts and does not maintain history between processes. Future improvements could add part-of-speech-aware lemmatization, richer intent detection, and a larger reviewed knowledge base.

## Example

```text
You: hello
Bot: Hello! Ask me about Python, NLP, or another topic in my knowledge base.
You: What is TF-IDF?
Bot: TF-IDF stands for term frequency-inverse document frequency and estimates how important a word is to a document collection.
You: history
You: reset
Bot: Conversation history cleared.
You: exit
Bot: Goodbye, take care!
```

## Credits

Created by `yuzaki_x_nasa` as an educational Python NLP project. NLTK and scikit-learn provide the local NLP and vectorization building blocks.
