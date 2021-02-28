import os
import random
import time

import pipwin as pipwin
import pyttsx3
import speech_recognition as sr
import requests
import pyaudio
#pip3 install rasa
#import rasa

def rasa():
    sender = input("What is your name?\n")

    bot_message = ""
    while bot_message != "Bye":
        message = input("What's your message?\n")

        print("Sending message now...")

        r = requests.post('http://192.168.0.138:5002/webhooks/rest/webhook', json={"sender": sender, "message": message})

        print("Bot says, ")
        for i in r.json():
            bot_message = i['text']
            print(f"{i['text']}")
def chatBot():
    import json
    import numpy as np
    from tensorflow import keras
    from sklearn.preprocessing import LabelEncoder

    import colorama
    colorama.init()
    from colorama import Fore, Style, Back

    import random
    import pickle

    with open("intents.json") as file:
        data = json.load(file)

    def chat():
        # load trained model
        model = keras.models.load_model('chat_model')

        # load tokenizer object
        with open('tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        while True:
            print(Fore.LIGHTBLUE_EX + "User: " + Style.RESET_ALL, end="")
            inp = input()
            if inp.lower() == "quit":
                break

            result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]),
                                                                              truncating='post', maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL, np.random.choice(i['responses']))

            # print(Fore.GREEN + "ChatBot:" + Style.RESET_ALL,random.choice(responses))

    print(Fore.YELLOW + "Start messaging with the bot (type quit to stop)!" + Style.RESET_ALL)
    chat()

def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def game():
    engine = pyttsx3.init()
    # set the list of words, maxnumber of guesses, and prompt limit
    WORDS = ["apple", "banana", "grape", "orange", "mango", "lemon"]
    NUM_GUESSES = 3
    PROMPT_LIMIT = 5
    # create recognizer and mic instances
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    # get a random word from the list
    word = random.choice(WORDS)
    # format the instructions string
    instructions = (
        "I'm thinking of one of these words:\n"
        "{words}\n"
        "You have {n} tries to guess which one.\n"
    ).format(words=', '.join(WORDS), n=NUM_GUESSES)
    # show instructions and wait 3 seconds before starting the game
    print(instructions)
    engine.say(instructions)
    engine.runAndWait()
    # time.sleep(3)
    for i in range(NUM_GUESSES):
        # get the guess from the user
        # if a transcription is returned, break out of the loop and
        #     continue
        # if no transcription returned and API request failed, break
        #     loop and continue
        # if API request succeeded but no transcription was returned,
        #     re-prompt the user to say their guess again. Do this up
        #     to PROMPT_LIMIT times
        for j in range(PROMPT_LIMIT):
            print('Guess {}. Speak!'.format(i + 1))
            guess = recognize_speech_from_mic(recognizer, microphone)
            if guess["transcription"]:
                break
            if not guess["success"]:
                break
            print("I didn't catch that. What did you say?\n")
            engine.say("I didn't catch that. What did you say?\n")
            engine.runAndWait()

        # if there was an error, stop the game
        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))
            break

        # show the user the transcription
        print("You said: {}".format(guess["transcription"]))
        engine.say("You said: {}".format(guess["transcription"]))
        engine.runAndWait()

        # determine if guess is correct and if any attempts remain
        guess_is_correct = guess["transcription"].lower() == word.lower()
        user_has_more_attempts = i < NUM_GUESSES - 1

        # determine if the user has won the game
        # if not, repeat the loop if user has more attempts
        # if no attempts left, the user loses the game

        if guess_is_correct:
            print("Correct! You win!".format(word))
            engine.say("Correct! You win!")
            engine.runAndWait()
            break
        elif user_has_more_attempts:
            print("Incorrect. Try again.\n")
            engine.say("Incorrect. Try again")
            engine.runAndWait()
        else:
            print("Sorry, you lose!\nI was thinking of '{}'.".format(word))
            engine.say("Sorry, you lose!\nI was thinking of '{}'.".format(word))
            engine.runAndWait()
            game()
            break


if __name__ == "__main__":
    chatBot()
    #game()