import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json", SCOPE
)

client = gspread.authorize(creds)

# CHANGE THIS to your actual sheet name
sheet = client.open("MCPSB Attendance Register").sheet1

def add_to_sheet(data):
    sheet.append_row(data)
