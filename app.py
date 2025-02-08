from fasthtml.common import *
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv() 

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def read_Emails(page: int):
    offset = page * 10
    response = supabase.table("Summaries") \
        .select("Summary,link,title") \
        .order("created_at", desc=True) \
        .range(offset, offset + 10).execute()  # Get 11 items to check for next page
        

    
    data = response.data
    has_next = len(data) > 10
    return data[:10] if has_next else data, has_next

app = FastHTML(hdrs=(picolink,))

def display_dictionary_list(data_list, current_page, has_next):
    buttons = []
    
    # Previous button (only show if not on first page)
    if current_page > 0:
        prev_page = current_page - 1
        buttons.append(
            A("← Previous", href=f"/?page={prev_page}", 
              cls="secondary outline", 
              style="margin-right: auto;")
        )
    
    # Next button (only show if more pages exist)
    if has_next:
        next_page = current_page + 1
        buttons.append(
            A("Next →", href=f"/?page={next_page}", 
              cls="secondary outline", 
              style="margin-left: auto;")
        )
    
    footer = []
    if buttons:
        footer = [
            Footer(
                Div(
                    *buttons,
                    style="display: flex; justify-content: space-between; margin-top: 1rem;"
                ),
                style="text-align: center;"
            )
        ]
    
    return Main(
        H1("Summaries", cls="heading"),
        *[create_container(item) for item in data_list],
        *footer,
        cls="container"
    )

def create_container(dictionary):
    return Article(
        Div(
            H3(dictionary['title'], cls="heading"),
            Pre(
                dictionary['Summary'],
                style="white-space: pre-wrap; word-wrap: break-word;"
            ),
            A(
                "Read More",
                href=dictionary['link'],
                target="_blank",
                cls="contrast outline"
            ),
            cls="overflow-auto"
        ),
        role="alert",
        cls="secondary"
    )

@app.route("/")
def get(request):
    try:
        page = int(request.query_params.get('page', 0))
    except ValueError:
        page = 0
    page = max(page, 0)  # Ensure page never goes below 0
    
    data, has_next = read_Emails(page)
    return display_dictionary_list(data, page, has_next)

serve()