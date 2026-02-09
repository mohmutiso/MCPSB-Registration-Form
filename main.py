from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import base64
import uuid

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure signature folder exists
os.makedirs("static/signatures", exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Google Sheets setup using Render secret file
SERVICE_ACCOUNT_PATH = "/run/secrets/service_account.json"

if not os.path.exists(SERVICE_ACCOUNT_PATH):
    raise FileNotFoundError(f"Service account JSON not found at {SERVICE_ACCOUNT_PATH}")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_PATH,
    scope
)

client = gspread.authorize(creds)
sheet = client.open("MCPSB Staff Attendance Register").sheet1

# ⭐ CHANGE THIS TO YOUR REAL RENDER URL
BASE_URL = "https://mcpsb-registration-form.onrender.com/"


# Serve form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Handle submission
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

    try:
        # Convert base64 signature to PNG image
        header, encoded = signature.split(",", 1)
        image_data = base64.b64decode(encoded)

        filename = f"{uuid.uuid4()}.png"
        filepath = f"static/signatures/{filename}"

        with open(filepath, "wb") as f:
            f.write(image_data)

        # Create public URL
        image_url = f"{BASE_URL}/static/signatures/{filename}"

        # Show image directly in Google Sheets
        sheet_image = f'=IMAGE("{image_url}")'

        # Prepare row
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
            sheet_image
        ]

        sheet.append_row(row)

        return {
            "status": "success",
            "message": "Attendance submitted successfully!"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
