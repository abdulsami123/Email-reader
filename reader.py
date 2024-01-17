import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pyttsx3
import util


    
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
    # Call the Gmail API to retrieve the latest email from a specific sender
    service = build("gmail", "v1", credentials=creds)
    response = service.users().messages().list(userId="me", q="from:hello@nicksingh.com", maxResults=1).execute()
    messages = []
    if "messages" in response:
        messages.extend(response["messages"])

    if not messages:
        print("No messages found.")
    else:
        latest_message_id = messages[0]["id"]
        latest_message = service.users().messages().get(userId="me", id=latest_message_id, format="full").execute()
        message_payload = latest_message["payload"]
        if "parts" in message_payload:
            for part in message_payload["parts"]:
                if part["mimeType"] == "text/plain":
                    message_text = part["body"]["data"]
                    message_text = base64.urlsafe_b64decode(message_text).decode("utf-8")
                    print(message_text)
                    util.read_out_loud(message_text)
                    break  # Stop after printing the first "text/plain" part
        else:
            print("No message parts found.")

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  main()
