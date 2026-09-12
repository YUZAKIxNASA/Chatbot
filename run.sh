#!/usr/bin/env sh
set -eu

command -v python3 >/dev/null 2>&1 || {
    echo "Python 3 is required." >&2
    exit 1
}

python3 -c "import nltk, sklearn" >/dev/null 2>&1 || {
    echo "Dependencies are missing. Run: python3 -m pip install -r requirements.txt" >&2
    exit 1
}

exec python3 main.py
