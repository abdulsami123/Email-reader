from fastapi import FastAPI, Query, Request , HTTPException , Body
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from schemas import Summaries,Bookmarks
from typing import List
import os
from pydantic import ValidationError
from datetime import datetime

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

@app.get("/items", response_class=HTMLResponse, response_model=List[Summaries])
async def get_items(
    request: Request,
    offset: int = Query(0),
    limit: int = Query(10),
):
    start = offset
    end = offset + limit -1
    query = supabase.table("Summaries").select("*").order("id", desc=True).range(start,end)
    data = query.execute().data

    # Validate response data against Pydantic model
    try:
        validated_data = [Summaries(**item) for item in data]
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    
    # Check for next page (more efficient than counting all rows)
    next_page_query = supabase.table("Summaries").select("*").order("id", desc=True).range(end + 1, end + 1) #Check if there is at least one more record after the current page
    next_page_data = next_page_query.execute().data
    has_next_page = len(next_page_data) > 0 #If there is at least one record then there is a next page

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": validated_data,
            "offset": offset,
            "limit": limit,
            "has_next_page": has_next_page,  # Pass this to the template
        }
    )


@app.post("/bookmarks")
async def post_bookmarks(item:Bookmarks , request:Request ):
    item = item.model_dump()
    
    try:
        # Insert the item into the Bookmarks table
        response = supabase.table("Bookmarks").insert(item).execute()
        
        # Check if the insertion was successful
        if response.data:
            return templates.TemplateResponse("index.html", {"request": request})
        else:
            raise HTTPException(status_code=400, detail="Failed to save bookmark")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/bookmarks-page")
async def get_bookmarks( request:Request):

    query = supabase.table("Bookmarks").select("*").order("id", desc=True)
    data = query.execute().data
    
    return templates.TemplateResponse(
        "bookmarks.html",
        {
            "request": request,
            "items": data,
        }
    )