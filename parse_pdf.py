"Creating a python script to parse a pdf and extract data"

from pypdf import PdfReader
from pathlib import Path
import polars as pl

reader = PdfReader("order1.pdf")
text = "\n\n".join(page.extract_text() or "" for page in reader.pages)

Path("output.txt").write_text(text, encoding="utf-8")
print("Saved as output.txt")

"Creating a python script to save the extracted data in a table format"


