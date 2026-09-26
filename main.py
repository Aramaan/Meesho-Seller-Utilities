import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import polars as pl

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

df = pl.DataFrame(
    {
        "source_file": ["Dinvoice_001.pdf", "Dinvoice_002.pdf"],
        "order_id": ["ORD-1001", "ORD-1002"],
        "Product": ["Kurta", "Saree"],
        "customer_name": ["Rohan Sharma", "Priya Verma"],
        "customer_address": ["12 Main Road, Delhi", "45 Park Street, Kolkata"],
        "customer_pincode": ["110001", "700001"],
        "order_number": ["A1001", "A1002"],
        "invoice_number": ["INV-9001", "INV-9002"],
        "order_date": ["2026-09-01", "2026-09-02"],
        "invoice_date": ["2026-09-01", "2026-09-02"],
        "size": ["M", "Free Size"],
        "quantity": [2, 1],
        "color": ["Blue", "Red"],
        "description": ["Cotton Kurta", "Silk Saree"],
        "gross_amount": [1499.0, 2499.0],
        "discount": [100.0, 200.0],
        "total_amount": [1399.0, 2299.0],
    }
)

def get_google_client():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return gspread.authorize(creds)

def update_google_sheet(df: pl.DataFrame, sheet_id: str, worksheet_name: str = "Sheet1"):
    if df.is_empty():
        print("No data to upload.")
        return

    client = get_google_client()
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)

    rows = [df.columns]
    for row in df.to_dicts():
        rows.append([row.get(col) for col in df.columns])

    worksheet.clear()
    worksheet.append_rows(rows, value_input_option="RAW")
    print(f"Uploaded {df.height} rows to Google Sheet")

update_google_sheet(df, "1Cpe5yE1yYNx6zkSHcnqiZU6QZjDqjuL18C_VbMHyZv4")