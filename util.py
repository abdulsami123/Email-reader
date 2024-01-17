import pyttsx3

def read_out_loud(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()