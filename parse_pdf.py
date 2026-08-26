import re
from pathlib import Path

import polars as pl
from pypdf import PdfReader
import utilities.utils as utils

# Folder containing the PDF files to be processed,
#  and the output folder for the extracted data.
PDF_DIR = Path("order_labels")
OUTPUT_DIR = Path("Tabular_data")
OUTPUT_DIR.mkdir(exist_ok=True)


def parse_pdf(pdf_path: Path) -> tuple:
    """Extract relevant information from a PDF file and return it as a tuple."""

    # Read and extract text from the PDF file.
    reader = PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Extract the customer address block from the text.
    customer_match = re.search(
        r"Customer Address\s+(.*?)\s+If undelivered, return to:",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    customer_block = customer_match.group(1).strip() if customer_match else ""

    customer_lines = [
        utils.clean(line)
        for line in customer_block.splitlines()
        if utils.clean(line)
    ]
    # Find the product section and its details.
    product_match = re.search(
        r"Product Details.*?SKU Size Qty Color Order No\.\s+"
        r"(?P<sku>\S+(?:\s+0)?)\s+"
        r"(?P<size>(?:(?:Un|Semi)\s+Stitched|Free\s+Size))\s+"
        r"(?P<quantity>\d+)\s+"
        r"(?P<color>\S+)\s+"
        r"(?P<item_order_number>\S+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    # Find the invoice section and its details.
    invoice_match = re.search(
        r"Description Qty Gross Amount Discount Total\s+"
        r"(?P<description>.*?)\s+(?P<invoice_quantity>\d+)\s+"
        r"Rs\.(?P<gross_amount>[\d,.]+)\s+"
        r"Rs\.(?P<discount>[\d,.]+)\s+"
        r"Rs\.(?P<total_amount>[\d,.]+)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    # halt processing if either the product or invoice section is not found.
    if not product_match:
        raise ValueError(f"Product row not found in {pdf_path.name}")

    if not invoice_match:
        raise ValueError(f"Invoice row not found in {pdf_path.name}")

    product = product_match.groupdict()
    invoice = invoice_match.groupdict()

    # Return a tuple containing the extracted data, utils.cleaned and formatted.
    return (
        pdf_path.name,                                                                                 # source_file
        product["item_order_number"],    
        product["sku"], 
        customer_lines[0] if customer_lines else None,                                                 # customer_name
        utils.clean(" ".join(customer_lines[1:])),                                                           # customer_address
        utils.first_match(r"Customer Address.*?\b(\d{6})\b", text, re.IGNORECASE | re.DOTALL),               # customer_pincode
        utils.first_match(r"BILL OF SUPPLY.*?Order No\.\s+([A-Za-z0-9]+)", text, re.IGNORECASE | re.DOTALL), # order_number
        utils.first_match(r"Invoice No\.\s+([A-Za-z0-9]+)", text, re.IGNORECASE),                            # invoice_number
        utils.first_match(r"Order Date\s+([0-9.]+)", text),                                                  # order_date
        utils.first_match(r"Invoice Date\s+([0-9.]+)", text),                                                # invoice_date                                                                               # sku
        product["size"],                                                                               # size
        int(product["quantity"]),                                                                      # quantity
        product["color"],                                                                              # color                                                              # item_order_number
        utils.clean(invoice["description"]),                                                                 # description
        utils.money(invoice["gross_amount"]),                                                                # gross_amount
        utils.money(invoice["discount"]),                                                                    # discount
        utils.money(invoice["total_amount"]),                                                                # total_amount
    )


frames = []

for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    try:
        frames.append(parse_pdf(pdf_path))
        print(f"Parsed: {pdf_path.name}")
    except ValueError as error:
        print(f"Skipped: {error}")

# Headers for the DataFrame columns, matching the order of the tuple returned by parse_pdf.
headers = [
    "source_file", "order_id", "Product", "customer_name", "customer_address", "customer_pincode",
    "order_number", "invoice_number", "order_date", "invoice_date",
     "size", "quantity", "color",
    "description", "gross_amount", "discount", "total_amount"
]

# Create a Polars DataFrame from the list of tuples, using the defined headers.
df = (
    pl.DataFrame(frames, schema=headers, orient="row")
    if frames
    else pl.DataFrame(schema=headers)
)


# Export the dataframe to CSV and JSON files and parquet and arrow formats
#  in the output directory.
def export_dataframe(df: pl.DataFrame, output_dir: Path) -> None:
    """Export the dataframe to various formats in the specified output directory."""
    df.write_csv(output_dir / "invoice_data.csv")
    df.write_json(output_dir / "invoice_data.json")
    df.write_ipc(output_dir / "invoice_data.arrow")
    df.write_parquet(output_dir / "invoice_data.parquet")
    utils.export_to_docx(df, output_dir / "invoice_data.docx")

export_dataframe(df, OUTPUT_DIR)

print(df.select(df.columns[:-5]))

print(f"Processed {df.height} PDF files.")

"""

"""
