# ⚡ EnergyBae Solar Load Calculator

AI-powered automation tool that converts electricity bills into solar-ready Excel reports.

## Features

- Upload PDF / Image electricity bill
- AI extracts:
  - Consumer name
  - Consumer number
  - Connection type
  - Sanctioned load
  - Fixed charges
  - Latest bill amount
  - 12 months unit history
- Auto-fills EnergyBae solar Excel template
- Preserves formulas
- Download completed Excel instantly

## Tech Stack

- Python
- Streamlit
- Gemini Vision API
- OpenPyXL
- PyMuPDF

## Project Structure

```text
energybae-ai/
│
├── app.py
├── requirements.txt
├── .env
│
├── templates/
│   └── E-Bill Analysis.xlsx
│
│
└── src/
    ├── extractor.py
    ├── excel_writer.py
    └── utils.py
```

## Setup

Install:

```bash
pip install -r requirements.txt
```

Add `.env`:

```env
GEMINI_API_KEY=your_key_here
```

Run:

```bash
streamlit run app.py
```

## Workflow

Upload bill → AI extraction → Excel auto-fill → Download report

## Author

John Victor Dabbakuti
