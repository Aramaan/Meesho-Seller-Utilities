# Meesho Order Data Processing (incomplete)

This project extracts order and invoice details from Meesho PDF order labels, exports the results to tabular formats, and generates an interactive map from geocoded locations. Made this for Meesho Sellers to keep track of their orders and facilitate  repeated fraud prevention.

(personal project made for my mom's online retail business which other sellers can use)

## Project Structure

```text
.
├── main.py
├── parse_pdf.py
├── map.html
├── order_labels/
├── Tabular_data/
│   ├── invoice_data.csv
│   ├── invoice_data.json
│   ├── invoice_data.arrow
│   ├── invoice_data.parquet
│   └── invoice_data.docx
└── utilities/
    ├── address_to_geocode.py
    ├── geocode_to_map.py
    ├── pincode_to_geocode.py
    └── utils.py
```

## Requirements

- Python 3.10 or later
- Meesho PDF order labels in `order_labels/`
- Internet access for geocoding and map tiles

Install the dependencies:

```bash
pip install polars pypdf python-docx folium googlemaps
```

## Extract Invoice Data

Place PDF order labels in `order_labels/`, then run:

```bash
python parse_pdf.py
```

The script extracts customer, address, PIN code, order, invoice, product, quantity, and payment information.

Generated files are saved in `Tabular_data/`:

- `invoice_data.csv`
- `invoice_data.json`
- `invoice_data.arrow` (Apache Arrow IPC format)
- `invoice_data.parquet` (Parquet columnar format)
- `invoice_data.docx`

The generated tabular files are ignored by Git because they are derived from
the PDF labels. The DOCX export is created by `export_to_docx` from
`utilities/utils.py`.

Utility functions can be imported with:

```python
import utilities.utils as utils
```

## Generate the Map

Run:

```bash
python utilities/geocode_to_map.py
```

This generates `map.html`. Open the file in a browser to view the interactive Leaflet map created by Folium.

## Geocoding Utilities

`utilities/pincode_to_geocode.py` provides:

- `pincode_to_latlong(pincode)`: converts an Indian PIN code into latitude and longitude
- `distance_km(...)`: calculates the distance between two coordinate pairs

Set the Google Maps API key before using the geocoding function.

Windows PowerShell:

```powershell
$env:GOOGLE_MAPS_API_KEY = "your-api-key"
```

Command Prompt:

```cmd
set GOOGLE_MAPS_API_KEY=your-api-key
```

## Notes

- Never commit API keys to the repository.
- Map tiles are loaded from OpenStreetMap.
- Check geocoded locations for accuracy before using them for delivery planning.
- `main.py` is reserved for future application orchestration.
