import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pyttsx3
import base64
import email_parser
from datetime import datetime


    
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

  #, q="TLDR <dan@tldrnewsletter.com>" 
  try:
    service = build("gmail", "v1", credentials=creds)
    response = service.users().messages().list(userId="me", q="from:dan@tldrnewsletter.com").execute()
    messages = response.get("messages", [])
    if not messages:
        print("No messages found.")
    else:
        latest_message_id = messages[0]["id"]
        latest_message = service.users().messages().get(userId="me", id=latest_message_id, format="full").execute()
        
        # Get the HTML part of the email
        html_part = None
        if 'payload' in latest_message and 'parts' in latest_message['payload']:
            for part in latest_message['payload']['parts']:
                if part['mimeType'] == 'text/html':
                    html_part = part
                    break
        # Extract timestamp (in milliseconds since epoch)
        email_timestamp = int(latest_message['internalDate'])
    
        # Convert to datetime object (UTC)
        date_time = datetime.datetime.utcfromtimestamp(email_timestamp / 1000)
    
        # Format as ISO string (optional)
        formatted_time = date_time.isoformat()
        
        if html_part:
            # Decode the HTML content
            html_content = base64.urlsafe_b64decode(html_part['body']['data']).decode('utf-8')
            
            # Extract links from the HTML content
            links = email_parser.extract_newsletter_links(html_content)
            
            # print("Extracted links:")
            # for link in links:
            #     print(link)
            return {'links':links, 'timestamp':formatted_time}
        else:
            return "No HTML content found in the email."



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
