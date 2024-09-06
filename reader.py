import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pyttsx3
import base64
from bs4 import BeautifulSoup


    
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  
  try:
    service = build("gmail", "v1", credentials=creds)
    response = service.users().messages().list(userId="me", q="TLDR <dan@tldrnewsletter.com> ").execute()
    messages = response.get("messages", [])
    if "messages" in response:
      messages.extend(response["messages"])
    if not messages:
        print("No messages found.")
    else:
        latest_message_id = messages[0]["id"]
        latest_message = service.users().messages().get(userId="me", id=latest_message_id, format="raw").execute()
        message_text = base64.urlsafe_b64decode(latest_message["raw"]).decode("utf-8")

        # Parse the message using BeautifulSoup
        soup = BeautifulSoup(message_text, "html.parser")

        # Find the body element
        body_element = soup.find("body")

        if body_element:
          
        # Extract text from the body element
          body_text = body_element.text
          return body_text
          
        else:
          print("Body element not found.")

  except HttpError as error:
      print(f"An error occurred: {error}")
      if error.resp.status == 401:
          print("Unauthorized. Check your credentials.")
      elif error.resp.status == 403:
          print("Forbidden. Check your permissions and scopes.")
      elif error.resp.status == 404:
          print("Not found. Check your query and user ID.")
      else:
          print(f"Unexpected error: {error.resp.status}")

  
  

if __name__ == "__main__":
  main()
