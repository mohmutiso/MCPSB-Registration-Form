from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# Enable CORS (optional, helpful during testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (HTML files)
templates = Jinja2Templates(directory="templates")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("MCPSB Staff Attendance Register").sheet1

# Serve the form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle form submission
@app.post("/submit-form/")
async def submit_form(
    title: str = Form(...),
    custom_title: str = Form(""),
    first_name: str = Form(...),
    surname: str = Form(...),
    other_names: str = Form(""),
    id_number: str = Form(...),
    designation: str = Form(...),
    organization: str = Form(...),
    gender: str = Form(...),
    pwd: str = Form(...),
    disability_category: str = Form(""),
    date: str = Form(...),
    time: str = Form(...),
    signature: str = Form(...),
    declaration: str = Form(...)
):
    # Use custom title if "Other" selected
    final_title = custom_title if title == "Other" else title

    # Prepare row for Google Sheets
    row = [
        final_title,
        first_name,
        surname,
        other_names,
        id_number,
        designation,
        organization,
        gender,
        pwd,
        disability_category,
        date,
        time,
        signature
    ]

    try:
        sheet.append_row(row)
        return {"status": "success", "message": "Attendance submitted successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
