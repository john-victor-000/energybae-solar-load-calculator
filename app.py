import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import tempfile

from src.extractor import extract_bill_data
from src.excel_writer import fill_excel_template
from src.utils import save_uploaded_file


# -----------------------
# Config
# -----------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATE_PATH = BASE_DIR / "templates" / "E-Bill Analysis.xlsx"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="EnergyBae Solar Load Calculator",
    page_icon="☀️",
    layout="wide"
)


# -----------------------
# Styling
# -----------------------
st.markdown("""
<style>
.main{
    background-color:#f7fff7;
}

/* title */
.title{
    text-align:center;
    color:#0a7f3f;
    font-size:42px;
    font-weight:700;
}

/* subtitle */
.subtitle{
    text-align:center;
    color:#666666;
    font-size:18px;
    margin-bottom:30px;
}

/* cards */
.green-box{
    background:#eaffea;
    padding:25px;
    border-radius:18px;
    border-left:8px solid #0a7f3f;
    box-shadow:0 6px 20px rgba(0,0,0,0.08);
    min-height:140px;
}

/* force heading color */
.green-box h4{
    color:#0a7f3f !important;
    font-size:32px;
    margin-bottom:12px;
    font-weight:700;
}

/* force paragraph color */
.green-box p{
    color:#222222 !important;
    font-size:20px;
    margin:0;
    font-weight:500;
}

.metric-card{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)


# -----------------------
# Header
# -----------------------
st.markdown(
    '<p class="title">⚡ EnergyBae Solar Load Calculator</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Upload electricity bill → AI extracts data → Excel auto-filled → Download report</p>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="green-box">
        <h4>📤 Upload Bill</h4>
        <p>PDF / JPG / PNG</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="green-box">
        <h4>🤖 AI Extraction</h4>
        <p>Read customer data</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="green-box">
        <h4>📥 Excel Output</h4>
        <p>Filled solar sheet</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# -----------------------
# Upload
# -----------------------
uploaded_file = st.file_uploader(
    "Upload Electricity Bill",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file:

    filepath = save_uploaded_file(uploaded_file, str(UPLOAD_DIR))

    st.success("File uploaded successfully ✅")

    # Preview image
    if filepath.lower().endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(filepath)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.image(
                image,
                caption="Uploaded Bill",
                width=350
            )

    if st.button("🚀 Generate Solar Report", use_container_width=True):

        progress = st.progress(0)

        with st.spinner("Reading bill..."):
            progress.progress(20)

            extracted = extract_bill_data(filepath)

        progress.progress(60)

        st.success("Data extracted successfully ✅")

        st.subheader("Extracted Information")

        c1, c2 = st.columns(2)

        with c1:
            st.info(f"**Consumer Name:** {extracted['consumer_name']}")
            st.info(f"**Consumer No:** {extracted['consumer_number']}")
            st.info(f"**Connection Type:** {extracted['connection_type']}")
            st.info(f"**Sanctioned Load:** {extracted['sanctioned_load']}")

        with c2:
            st.info(f"**Fixed Charges:** ₹{extracted['fixed_charges']}")
            st.info(f"**Latest Bill Amount:** ₹{extracted['latest_bill_amount']}")
            st.info(f"**12 Month Units:** {len(extracted['monthly_units'])} months")

        st.subheader("Monthly Units")
        st.table(extracted["monthly_units"])

        progress.progress(80)

        output_file = fill_excel_template(
        str(TEMPLATE_PATH),
        extracted,
        str(OUTPUT_DIR)
)

        progress.progress(100)

        st.success("Solar Excel generated successfully ✅")

        with open(output_file, "rb") as f:
            st.download_button(
                label="⬇ Download Filled Excel",
                data=f,
                file_name="EnergyBae_Solar_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
