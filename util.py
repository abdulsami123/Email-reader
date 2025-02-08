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
    
  
def load_api_key(x):
    """_summary_
        pass something like this to the function "gemini-api-key.json"
    Args:
        x (_type_): _description_ 
        this will take the json object that contains the required api
    """
    try:
        with open(Path(__file__).parent / x) as f:
            os.environ["api-key"] = json.load(f)["api-key"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Error loading API key: {e}")
        
        

def extract_text(article_url):
    g = Goose()
    article = g.extract(article_url)
    return article.cleaned_text, article.title

def extract_title(x):
    url = x

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("title").text
    return title



        