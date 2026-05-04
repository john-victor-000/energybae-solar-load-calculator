import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv
from PIL import Image
import fitz  # PyMuPDF

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def pdf_to_image(pdf_path):
    """
    Convert first page PDF -> PIL Image
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    img = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    return img


def load_bill(file_path):
    """
    Load PDF / image
    """
    ext = file_path.lower().split(".")[-1]

    if ext == "pdf":
        return pdf_to_image(file_path)

    return Image.open(file_path)


def clean_number(value, default=0):
    """
    Convert messy Gemini numeric output safely.
    Examples:
    ₹1,460 -> 1460
    3.30 KW -> 3.30
    "" -> 0
    None -> 0
    """
    if value is None:
        return default

    value = str(value).strip()

    if value == "":
        return default

    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("Rs.", "")
    value = value.replace("Rs", "")
    value = value.replace("kW", "")
    value = value.replace("KW", "")
    value = value.strip()

    value = re.sub(r"[^\d.]", "", value)

    if value == "":
        return default

    try:
        return float(value)
    except Exception:
        return default


def extract_bill_data(file_path):
    """
    Extract electricity bill details using Gemini Vision
    """

    image = load_bill(file_path)

    prompt = """
You are an expert electricity bill parser.

Read Maharashtra MSEDCL electricity bill carefully.

Return STRICT JSON only.

{
  "consumer_name":"",
  "consumer_number":"",
  "connection_type":"",
  "sanctioned_load":"",
  "fixed_charges":"",
  "latest_bill_amount":"",
  "monthly_units":[]
}

Rules:
- Extract EXACT connection type text
- Example: 90/LT I Res 1-Phase
- monthly_units must have exactly 12 integers
- No explanation
- JSON only
- Missing numeric values -> 0
"""

    response = model.generate_content([prompt, image])

    text = response.text.strip()

    # remove markdown formatting
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    try:
        data = json.loads(text)
    except Exception:
        # fallback structure
        data = {
            "consumer_name": "",
            "consumer_number": "",
            "connection_type": "",
            "sanctioned_load": 0,
            "fixed_charges": 0,
            "latest_bill_amount": 0,
            "monthly_units": [0] * 12
        }

    # normalize numbers safely
    data["fixed_charges"] = clean_number(data.get("fixed_charges"))

    if data["fixed_charges"] == 0:
        data["fixed_charges"] = round(
            clean_number(data.get("latest_bill_amount")) * 0.04,
            2
        )
    data["latest_bill_amount"] = clean_number(data.get("latest_bill_amount"))
    data["sanctioned_load"] = clean_number(data.get("sanctioned_load"))

    # normalize monthly units
    monthly = data.get("monthly_units", [])

    cleaned_monthly = []
    for x in monthly:
        try:
            x = str(x).replace(",", "").strip()
            cleaned_monthly.append(int(float(x)))
        except Exception:
            cleaned_monthly.append(0)

    # ensure exactly 12 months
    if len(cleaned_monthly) < 12:
        cleaned_monthly = ([0] * (12 - len(cleaned_monthly))) + cleaned_monthly

    cleaned_monthly = cleaned_monthly[:12]

    data["monthly_units"] = cleaned_monthly

    return data