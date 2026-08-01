import os
import random
import string
import warnings

warnings.filterwarnings("ignore")

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

for pkg in ["punkt", "punkt_tab", "wordnet", "omw-1.4"]:
    try:
        nltk.data.find(pkg)
    except LookupError:
        nltk.download(pkg, quiet=True)

from nltk.stem import WordNetLemmatizer


KNOWLEDGE_BASE = """
Python is a high level general purpose programming language.
Python was created by Guido van Rossum and released in 1991.
Python supports multiple programming paradigms including procedural, object oriented and functional programming.
NLP stands for Natural Language Processing.
NLP is a field of artificial intelligence that gives machines the ability to read, understand and derive meaning from human language.
Common NLP tasks include tokenization, stemming, lemmatization, part of speech tagging and named entity recognition.
A chatbot is a software application used to conduct an online chat conversation via text or text to speech.
Machine learning is a subset of artificial intelligence that allows systems to learn from data.
Deep learning is a subset of machine learning based on artificial neural networks.
TF-IDF stands for term frequency inverse document frequency and is used to measure how important a word is to a document in a collection.
Cosine similarity is a metric used to measure how similar two documents are irrespective of their size.
"""

GREETING_INPUTS = ("hello", "hi", "greetings", "hey", "what's up", "sup")
GREETING_RESPONSES = [
    "Hi there, how can I help you today",
    "Hello, ask me anything from my knowledge base",
    "Hey, what would you like to know",
]

FAREWELL_INPUTS = ("bye", "goodbye", "exit", "quit", "see you")

lemmatizer = WordNetLemmatizer()
punctuation_remover = dict((ord(punct), None) for punct in string.punctuation)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def lem_tokens(tokens):
    return [lemmatizer.lemmatize(token) for token in tokens]


def lem_normalize(text):
    text = text.lower().translate(punctuation_remover)
    return lem_tokens(nltk.word_tokenize(text))


def check_greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
    return None


def check_farewell(sentence):
    for word in sentence.split():
        if word.lower() in FAREWELL_INPUTS:
            return True
    return False


def generate_response(user_input, sentence_list):
    bot_response = ""
    sentence_list.append(user_input)

    vectorizer = TfidfVectorizer(tokenizer=lem_normalize)
    tfidf = vectorizer.fit_transform(sentence_list)

    similarity_scores = cosine_similarity(tfidf[-1], tfidf)
    best_match_index = similarity_scores.argsort()[0][-2]

    flattened_scores = similarity_scores.flatten()
    flattened_scores.sort()
    best_score = flattened_scores[-2]

    sentence_list.pop()

    if best_score == 0:
        bot_response = "I am sorry, I do not understand that yet. Try asking about Python, NLP or chatbots."
    else:
        bot_response = sentence_list[best_match_index]

    return bot_response


def main():
    raw_sentences = nltk.sent_tokenize(KNOWLEDGE_BASE)
    raw_sentences = [s.strip() for s in raw_sentences if s.strip()]

    clear_screen()
    print("=" * 70)
    print("Hello Everyone It Me Your NLP Chatbot I am Created By Shahzaib Malik ")
    print("Type your question below. Type 'clear' to clear screen. Type 'bye' to exit.")
    print("=" * 70)

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "clear":
            clear_screen()
            continue

        if check_farewell(user_input):
            print("Bot: Goodbye, take care")
            break

        greeting = check_greeting(user_input)
        if greeting:
            print(f"Bot: {greeting}")
            continue

        if "thank" in user_input.lower():
            print("Bot: You are welcome")
            continue

        response = generate_response(user_input, raw_sentences.copy())
        print(f"Bot: {response}")


if __name__ == "__main__":
    main()
