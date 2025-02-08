from fasthtml.common import *
import os
import subprocess
import time
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv() 

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Initialize app FIRST
app = FastHTML(hdrs=(picolink,))  # ← Moved up before route definitions

# Track refresh status
refresh_status = {"running": False, "completed": False}

@app.route("/refresh", methods=["POST"])
def refresh_script(request):
    if refresh_status["running"]:
        return JSONResponse({"status": "error", "message": "Refresh already in progress"}, status_code=400)
    
    def run_script():
        try:
            refresh_status.update({"running": True, "completed": False})
            result = subprocess.run(["python", "gemini_reader.py"], check=True, capture_output=True, text=True)
            refresh_status.update({"running": False, "completed": True})
        except Exception as e:
            refresh_status.update({"running": False, "completed": False})
    
    # Run in background thread
    threading.Thread(target=run_script).start()
    return JSONResponse({"status": "started", "message": "Refresh process initiated"})

@app.route("/refresh-status")
def refresh_status_check(request):
    return JSONResponse(refresh_status)


def read_Emails(page: int):
    offset = page * 10
    response = supabase.table("Summaries") \
        .select("Summary,link,title") \
        .order("created_at", desc=True) \
        .range(offset, offset + 10).execute()
    
    data = response.data
    has_next = len(data) > 10
    return data[:10] if has_next else data, has_next

def display_dictionary_list(data_list, current_page, has_next):
    buttons = []
    
    # Previous button
    if current_page > 0:
        prev_page = current_page - 1
        buttons.append(
            A("← Previous", href=f"/?page={prev_page}", 
              cls="secondary outline", 
              style="margin-right: 0.5rem;")
        )
    
    # Next button
    if has_next:
        next_page = current_page + 1
        buttons.append(
            A("Next →", href=f"/?page={next_page}", 
              cls="secondary outline", 
              style="margin-left: 0.5rem;")
        )
    
    # Header with title and refresh button
    header = Div(
        H1("Summaries", cls="heading", style="flex-grow: 1;"),
        Button("🔄 Refresh", 
               onclick="startRefresh()",
               cls="contrast outline",
               style="margin-left: auto;"),
        style="display: flex; align-items: center; margin-bottom: 2rem;"
    )
    
    # Footer with navigation buttons
    footer = []
    if buttons:
        footer = [
            Footer(
                Div(
                    *buttons,
                    style="display: flex; justify-content: center; gap: 1rem; margin-top: 2rem;"
                ),
                style="text-align: center;"
            )
        ]
    
    return Main(
        header,
        Div(
            *[create_container(item) for item in data_list],
            style="display: grid; gap: 1.5rem;"
        ),
        *footer,
        cls="container",
        style="padding: 2rem; max-width: 800px; margin: 0 auto;",
        children=[
            Script("""
                let checkInterval;
                
                function startRefresh() {
                    const btn = document.querySelector('button[onclick="startRefresh()"]');
                    btn.innerHTML = '⏳ Processing...';
                    btn.disabled = true;
                    
                    fetch('/refresh', { method: 'POST' })
                        .then(response => {
                            if (!response.ok) throw new Error('Start failed');
                            checkInterval = setInterval(checkRefreshStatus, 2000);
                        })
                        .catch(handleRefreshError);
                }

                function checkRefreshStatus() {
                    fetch('/refresh-status')
                        .then(response => response.json())
                        .then(data => {
                            if (!data.running && data.completed) {
                                clearInterval(checkInterval);
                                window.location.reload();
                            } else if (!data.running && !data.completed) {
                                handleRefreshError(new Error('Refresh failed'));
                            }
                        })
                        .catch(handleRefreshError);
                }

                function handleRefreshError(error) {
                    clearInterval(checkInterval);
                    const btn = document.querySelector('button[onclick="startRefresh()"]');
                    btn.innerHTML = '🔄 Refresh';
                    btn.disabled = false;
                    alert(error.message);
                    console.error('Refresh error:', error);
                }
            """)
        ]
    )

# Rest of the code remains the same...
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