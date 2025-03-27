import pyttsx3
import json
from pathlib import Path
import os
from goose3 import Goose
import requests
from bs4 import BeautifulSoup

def read_out_loud(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
        
        

def extract_text(article_url):
    try:
        g = Goose()
        article = g.extract(article_url)
        return article.cleaned_text
    except Exception as e:
        print(f"Error extracting text from URL: {e}")
        return None

def extract_title(x):
    url = x

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        # Attempt to find the <title> tag
        title_tag = soup.find("title")
        if title_tag is not None:  # Check if the <title> tag was found
            return title_tag.text
        else:
            return "Title not found"
    except Exception as e:  # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")
        return "Title Unknown"





        