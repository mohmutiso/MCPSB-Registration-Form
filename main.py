from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = FastAPI()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Static + Templates
# -------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# -------------------------
# FIND SERVICE ACCOUNT FILE (SMART SEARCH)
# -------------------------

POSSIBLE_PATHS = [
    "/run/secrets/service_account.json",  # Render secret file
    "service_account.json"                # Local development fallback
]

SERVICE_ACCOUNT_PATH = None

for path in POSSIBLE_PATHS:
    if os.path.exists(path):
        SERVICE_ACCOUNT_PATH = path
        print(f"✅ Using service account at: {path}")
        break

if SERVICE_ACCOUNT_PATH is None:
    print("❌ Service account file NOT FOUND")
    raise Exception("Service account JSON missing. Check Render Secret Files.")

# -------------------------
# Google Sheets
# -------------------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_PATH, scope
)

client = gspread.authorize(creds)
sheet = client.open("MCPSB Staff Attendance Register").sheet1

# -------------------------
# ROUTES
# -------------------------

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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

    final_title = custom_title if title == "Other" else title

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
