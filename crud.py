import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import pytz
import json

# Get current time in UTC
utc_now = datetime.now(pytz.utc)

# Format the timestamp with time zone
current_time = utc_now.isoformat()


load_dotenv() 

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(url, key)


def update_Emails(links,email_ts):
    response = (
    supabase.table("Emails")
    .insert({ "created_at": current_time , "links" : links , "vendor" : "TLDR" ,"email_reception_time":email_ts})
    .execute()
                )
    
def update_Summary(summary,link,title):
    response = (
    supabase.table("Summaries")
    .insert({ "created_at": current_time , "summary" : summary , "vendor" : "TLDR" , "link":link , "title":title})
    .execute()
                ) 
    
def read_Emails():
    response = supabase.table("Summaries") \
    .select("summary") \
    .order("created_at", desc=True) \
    .limit(10) \
    .execute()
    
    return response.data


def select_links():
    response = supabase.table("Emails").select("links").order("id", desc=True).limit(1).execute()
    data = response.data
    link_string = data[0]['links']
    parsed_links = json.loads(link_string) 
    
    
    return parsed_links




    







