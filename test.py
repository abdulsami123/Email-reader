from supabase import create_client, Client
import os

# Supabase configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_items(offset: int ,limit: int ):
    query = supabase.table("Summaries").select("*").range(offset, offset + limit - 1)
    data = query.execute().data
    print(data)

get_items(0,10)