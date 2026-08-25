import re
from pathlib import Path

import polars as pl
from docx import Document
from pypdf import PdfReader


# Clean extra whitespace and return a readable value.
def clean(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip()


# Convert an amount such as "1,496.00" into a float.
def money(value: str) -> float:
    return float(value.replace(",", ""))


# Return the first captured value found by a regular expression.
def first_match(pattern: str, text: str, flags: int = 0) -> str | None:
    match = re.search(pattern, text, flags)
    return clean(match.group(1)) if match else None


# Folder containing all PDF order files.
PDF_DIR = Path("order_labels")


def parse_pdf(pdf_path: Path) -> dict:
    """Extract order, customer, product, and invoice data from one PDF."""

    # Read and combine the text from all pages in the PDF.
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Save extracted text to inspect PDFs with a different layout.
    # if pdf_path.stem == "order2":
    #     Path("order2_extracted.txt").write_text(text, encoding="utf-8")

    # Extract the customer section, including multiple address lines.
    customer_match = re.search(
        r"Customer Address\s+(.*?)\s+If undelivered, return to:",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    customer_block = customer_match.group(1).strip() if customer_match else ""

    customer_lines = [
        clean(line)
        for line in customer_block.splitlines()
        if clean(line)
    ]
    # Find the product table row.
    product_match = re.search(
        r"Product Details.*?SKU Size Qty Color Order No\.\s+"
        r"(?P<sku>\S+(?:\s+0)?)\s+"
        r"(?P<size>(?:Un|Semi)\s+Stitched)\s+"
        r"(?P<quantity>\d+)\s+"
        r"(?P<color>\S+)\s+"
        r"(?P<item_order_number>\S+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    # Find the invoice item and its financial values.
    invoice_match = re.search(
        r"Description Qty Gross Amount Discount Total\s+"
        r"(?P<description>.*?)\s+(?P<invoice_quantity>\d+)\s+"
        r"Rs\.(?P<gross_amount>[\d,.]+)\s+"
        r"Rs\.(?P<discount>[\d,.]+)\s+"
        r"Rs\.(?P<total_amount>[\d,.]+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    # Stop processing this file if required data was not found.
    if not product_match:
        raise ValueError(f"Product row not found in {pdf_path.name}")

    if not invoice_match:
        raise ValueError(f"Invoice row not found in {pdf_path.name}")

    product = product_match.groupdict()
    invoice = invoice_match.groupdict()

    # Build one dictionary representing one PDF order.
    return {
        "source_file": pdf_path.name,
        "customer_name": customer_lines[0] if customer_lines else None,
        "customer_address": clean(" ".join(customer_lines[1:])),
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
        "order_date": first_match(r"Order Date\s+([0-9.]+)", text),
        "invoice_date": first_match(r"Invoice Date\s+([0-9.]+)", text),
        "sku": product["sku"],
        "size": product["size"],
        #"stitch_type": clean(product["stitch_type"]),
        "quantity": int(product["quantity"]),
        "color": product["color"],
        "item_order_number": product["item_order_number"],
        "description": clean(invoice["description"]),
        "gross_amount": money(invoice["gross_amount"]),
        "discount": money(invoice["discount"]),
        "total_amount": money(invoice["total_amount"]),
    }



# Parse every PDF and store each order as a separate dictionary.
records = []

for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    try:
        records.append(parse_pdf(pdf_path))
        print(f"Parsed: {pdf_path.name}")
    except ValueError as error:
        print(f"Skipped: {error}")


# Convert all parsed orders into a Polars dataframe.
df = pl.DataFrame(records)
print(df)


# Export the dataframe to CSV and JSON files.
df.write_csv("invoice_data.csv")
df.write_json("invoice_data.json")


# Create a DOCX document containing the dataframe as a table.
document = Document()
document.add_heading("Invoice Data", level=1)

table = document.add_table(rows=1, cols=len(df.columns))
table.style = "Table Grid"

# Add dataframe column names as the table header.
for index, column in enumerate(df.columns):
    table.rows[0].cells[index].text = column

# Add one DOCX table row for each PDF order.
for row in df.iter_rows(named=True):
    cells = table.add_row().cells

    for index, column in enumerate(df.columns):
        cells[index].text = str(row[column] or "")


# Save the completed DOCX file.
document.save("invoice_data.docx")

print(f"Processed {df.height} PDF files.")