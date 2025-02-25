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

#App startup
app = FastAPI()


#This is to indicate to the Templating engine where HTML template is
templates = Jinja2Templates(directory="templates")

# Supabase configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#Each Folder needs to be 'mounted' to make FastAPI aware of its existence in the directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/artifacts", StaticFiles(directory="artifacts"), name="artifacts")

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

# This is to Bookmark posts
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

# This is to render the Bookmarks button  
@app.get("/bookmarks-page")
async def get_bookmarks(request: Request, offset: int = Query(0), limit: int = Query(10)):
    try:
        start = offset
        end = offset + limit - 1
        
        # Fetch main data
        query = supabase.table("Bookmarks").select("*").order("id", desc=True).range(start, end)
        data = query.execute().data
        
        # Validate data
        validated_data = [Bookmarks(**item) for item in data]
        
        # Check for next page
        next_page_query = supabase.table("Bookmarks").select("*").order("id", desc=True).range(end + 1, end + 1)
        next_page_data = next_page_query.execute().data
        has_next_page = len(next_page_data) > 0
        
        # Determine if this is an HTMX request
        # this is important since the first request is a result of redirection and not a GET request    
        #it renders Bookmarks.html for redirects and then progressively renders using bookmarks_content.html using %include%
        is_htmx = request.headers.get("HX-Request") == "true"
        template_name = "bookmarks_content.html" if is_htmx else "bookmarks.html"
        
        return templates.TemplateResponse(
            template_name,
            {
                "request": request,
                "items": validated_data,
                "offset": offset,
                "limit": limit,
                "has_next_page": has_next_page,
            }
        )
        
    except Exception as e:
        print(f"Error in get_bookmarks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))