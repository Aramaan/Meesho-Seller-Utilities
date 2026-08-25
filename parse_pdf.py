import re
from pathlib import Path

import polars as pl
from docx import Document
from pypdf import PdfReader


PDF_FILE = "order_labels/order1.pdf"
TEXT_FILE = "output.txt"


def clean(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip()


def money(value: str) -> float:
    return float(value.replace(",", ""))


def first_match(pattern: str, text: str, flags: int = 0) -> str | None:
    match = re.search(pattern, text, flags)
    return clean(match.group(1)) if match else None


reader = PdfReader(PDF_FILE)
text = "\n".join(page.extract_text() or "" for page in reader.pages)
Path(TEXT_FILE).write_text(text, encoding="utf-8")

product_match = re.search(
    r"Product Details.*?SKU Size Qty Color Order No\.\s+"
    r"(?P<sku>\S+)\s+"
    r"(?P<size>\S+)\s+"
    r"(?P<stitch_type>Un\s+Stitched)\s+"
    r"(?P<quantity>\d+)\s+"
    r"(?P<color>\S+)\s+"
    r"(?P<item_order_number>\S+)",
    text,
    flags=re.IGNORECASE | re.DOTALL,
)

invoice_match = re.search(
    r"Description Qty Gross Amount Discount Total\s+"
    r"(?P<description>.*?)\s+"
    r"(?P<invoice_quantity>\d+)\s+"
    r"Rs\.(?P<gross_amount>[\d,.]+)\s+"
    r"Rs\.(?P<discount>[\d,.]+)\s+"
    r"Rs\.(?P<total_amount>[\d,.]+)",
    text,
    flags=re.IGNORECASE | re.DOTALL,
)

if not product_match:
    raise ValueError("Product row could not be found.")

if not invoice_match:
    raise ValueError("Invoice row could not be found.")

product = product_match.groupdict()
invoice = invoice_match.groupdict()

record = {
    "customer_name": first_match(
        r"Customer Address\s+([^\n]+)", text, re.IGNORECASE
    ),
    "customer_address": first_match(
        r"Customer Address\s+(.*?)\s+If undelivered, return to:",
        text,
        re.IGNORECASE | re.DOTALL,
    ),
    "customer_pincode": first_match(
        r"Customer Address.*?\b(\d{6})\b",
        text,
        re.IGNORECASE | re.DOTALL,
    ),
    "order_number": first_match(
        r"BILL OF SUPPLY.*?Order No\.\s+([A-Za-z0-9]+)",
        text,
        re.IGNORECASE | re.DOTALL,
    ),
    "invoice_number": first_match(
        r"Invoice No\.\s+([A-Za-z0-9]+)", text, re.IGNORECASE
    ),
    "order_date": first_match(
        r"Order Date\s+([0-9.]+)", text, re.IGNORECASE
    ),
    "invoice_date": first_match(
        r"Invoice Date\s+([0-9.]+)", text, re.IGNORECASE
    ),
    "sku": product["sku"],
    "size": product["size"],
    "stitch_type": clean(product["stitch_type"]),
    "quantity": int(product["quantity"]),
    "color": product["color"],
    "item_order_number": product["item_order_number"],
    "description": clean(invoice["description"]),
    "gross_amount": money(invoice["gross_amount"]),
    "discount": money(invoice["discount"]),
    "total_amount": money(invoice["total_amount"]),
}

df = pl.DataFrame([record])

print(df)

df.write_csv("invoice_data.csv")
df.write_json("invoice_data.json")

document = Document()
document.add_heading("Invoice Data", level=1)

table = document.add_table(rows=1, cols=len(df.columns))
table.style = "Table Grid"

for index, column in enumerate(df.columns):
    table.rows[0].cells[index].text = column

for row in df.iter_rows(named=True):
    cells = table.add_row().cells

    for index, column in enumerate(df.columns):
        cells[index].text = str(row[column] if row[column] is not None else "")

document.save("invoice_data.docx")

print("Created:")
print("- output.txt")
print("- invoice_data.csv")
print("- invoice_data.json")
print("- invoice_data.docx")