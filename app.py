import streamlit as st
import base64
from fpdf import FPDF

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    # This splits the text so it doesn't run off the page
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output()

# 1. Your SVG Code as a string
svg_code = """
<svg xmlns="http://w3.org" viewBox="0 0 240 80" width="240" height="80">
  <rect x="0" y="0" width="240" height="80" fill="#ffffff" rx="12" ry="12"/>
  <g transform="translate(20,40)">
    <circle cx="0" cy="0" r="24" fill="#0A74DA"/>
    <circle cx="8" cy="-6" r="12" fill="#ffffff"/>
  </g>
  <text x="70" y="48" font-family="Arial" font-size="36" font-weight="600" fill="#222222">SOP</text>
  <text x="70" y="70" font-family="Arial" font-size="14" fill="#555555">AI Generator</text>
</svg>
"""

# 2. Function to display it
def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    return f'data:image/svg+xml;base64,{b64}'

logo_url = render_svg(svg_code)

# 3. Use it in the sidebar
st.sidebar.image(logo_url, width=150)

# 4. Use it in the main header
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo_url, width=60)
with col2:
    st.title("Professional SOP Generator")

with st.sidebar:
    st.title("How to use")
    st.info("""
    1. Enter a clear **Topic**.
    2. Paste any **raw notes** or transcripts.
    3. Click **Generate SOP**.
    4. Copy the result into your document!
    """)
    import streamlit as st
import os
from groq import Groq
from fpdf import FPDF

# --- STEP 1: PDF Function ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    # Encoding prevents errors with special characters
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output()

# --- STEP 2: Initialize Groq ---
# Ensure you have 'GROQ_API_KEY' set in your Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("SOP Generator (Powered by Groq)")

topic = st.text_input("SOP Topic", placeholder="e.g., Data Security Protocol")
notes = st.text_area("Input Notes")

# --- STEP 3: Generation Logic ---if st.button("Generate SOP"):
    if topic or raw_notes:
        with st.spinner("Writing with Groq AI..."):
            try:
                # NEW GROQ GENERATION CODE
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",  # Fast and reliable model
                    messages=[
                        {"role": "system", "content": "You are a professional technical writer."},
                        {"role": "user", "content": f"Write an SOP for {topic}. Notes: {raw_notes}"}
                    ],
                    temperature=0.7
                )
                
                # Extract the text from the Groq response
                sop_text = completion.choices[0].message.content
                
                # Display Results
                st.subheader("Generated SOP")
                st.markdown(sop_text)
                
                # PDF Download (Indented same as above)
                pdf_bytes = create_pdf(sop_text)
                st.download_button("📥 Download PDF", pdf_bytes, f"{topic}.pdf")
                
            except Exception as e:
                st.error(f"Something went wrong: {e}")

