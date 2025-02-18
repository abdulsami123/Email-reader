from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
import os

app = FastAPI()

# Templates configuration
templates = Jinja2Templates(directory="templates")

# Supabase configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/items", response_class=HTMLResponse)
async def get_items(
    request: Request,
    offset: int = Query(0),
    limit: int = Query(10),
):
    start = offset
    end = offset + limit -1
    query = supabase.table("Summaries").select("*").order("id", desc=True).range(start,end)
    data = query.execute().data

    # Check for next page (more efficient than counting all rows)
    next_page_query = supabase.table("Summaries").select("*").order("id", desc=True).range(end + 1, end + 1) #Check if there is at least one more record after the current page
    next_page_data = next_page_query.execute().data
    has_next_page = len(next_page_data) > 0 #If there is at least one record then there is a next page

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": data,
            "offset": offset,
            "limit": limit,
            "has_next_page": has_next_page,  # Pass this to the template
        }
    )
