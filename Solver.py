# Score = (freq in letters in words * weight) + (word freq * weight)
import json
import string

import numpy as np
import requests
import time
import requests_cache

requests_cache.install_cache()

_wait = 0.1

def does_match_key(word, guess, word_key):
    for letter in word_key:
        letter = letter.lower()
        if letter != '_':
            if word.count(letter) < word_key.lower().count(letter) or word.count(letter) == 0:
                return False
    for i in range(len(word)):
        if word_key[i] != '_':
            if word_key[i].islower():
                if word_key[i] == word[i]:
                    return False
            if word_key[i].isupper():
                if word_key[i].lower() != word[i]:
                    return False
        else:
            if word.count(guess[i]) != 0 and word_key.lower().count(guess[i]) == 0:
                return False
            elif word.count(guess[i]) < word_key.lower().count(guess[i]):
                return False
    return True


def sigmoid(val, d, c):
    return 1 / (1 + (np.exp(1) ** (-d * (val - c))))


def get_freq(term):
    response = None
    while True:
        try:
            response = requests.get('https://api.datamuse.com/words?sp=' + term + '&md=f&max=1').json()
            if not getattr(response, 'from_cache', False):
                time.sleep(0.1)
        except:
            print('Could not get response. Sleep and retry...')
            time.sleep(_wait)
            continue
        break
    freq = 0.0 if len(response) == 0 else float(response[0]['tags'][0][2:])
    return freq


def calc_letter_freq(words_input, letters_input):
    for letter in letters_input:
        freq = 0
        for word in words_input:
            freq += word.count(letter)
        letters_input[letter] = freq
    return letters_input


def calc_word_score(words_input, letters_input):
    for word in words_input:
        letter_score = 0
        r = 0
        word_no_dups = "".join(set(word))
        if len(word_no_dups) < len(word):
            r = -0.01
        for letter in word_no_dups:
            letter_score += letters_input[letter]
        if words_input[word]["freq"] == 0:
            words_input[word]["freq"] = get_freq(word)
        words_input[word]["score"] = sigmoid(words_input[word]["freq"], 0.00005, 1863) + sigmoid(letter_score,
                                                                                                 0.002,
                                                                                                 800) + r
    return words_input


def get_best_guesses(words_input, num_guesses):
    index = 0
    top_scores = [val['score'] for val in words_input.values()]
    top_scores.sort(reverse=True)
    top_scores = top_scores[0:num_guesses]
    best_guesses = []
    for score in top_scores:
        best_guesses.append({[word for (word, value) in words_input.items() if value['score'] == score][0]: score})
    return best_guesses


def make_guess(guess, word_key, words_input):
    try:
        words_input.pop(guess)
    except:
        print("Not in current word list.")
    cpy = words_input.copy()
    for word in cpy:
        if not does_match_key(word, guess, word_key):
            words_input.pop(word)
    return words_input


def add_word(word, words_input):
    try:
        words_input[word]
    except:
        print("Adding word: ", word)
        words_input[word] = {"freq": 0, "score": 0}


class Solver:

    words = {
        "word": {"freq": 2, "score": 10}
    }

    letters = {letter: 0 for letter in list(string.ascii_lowercase)}

    possibleWords = None

    def __init__(self):
        with open("dictSorted.json", "r") as file:
            self.possibleWords = json.load(file)

    def make_guess(self, guess, word_key):
        self.possibleWords = make_guess(guess, word_key, self.possibleWords)
        return self.possibleWords

    def solve(self):
        # max: 1375 min: 37
        self.letters = calc_letter_freq(self.possibleWords, self.letters)
        # max: 3726 min: 0
        self.possibleWords = calc_word_score(self.possibleWords, self.letters)
        # Init game
        while True:
            print("Best guesses: ", get_best_guesses(self.possibleWords, 5))
            while True:
                guess = input("Guessed word: ")
                if (len(guess) != 5) or guess.count('_') > 0:
                    print("Not a 5 letter word.")
                else:
                    break
            while True:
                word_key = input("Word key: ")
                if len(word_key) != 5:
                    print("Not a 5 letter word key.")
                else:
                    break
            self.possibleWords = make_guess(guess, word_key, self.possibleWords)
