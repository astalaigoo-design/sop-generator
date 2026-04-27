import os
import base64

import streamlit as st
import base64
from fpdf import FPDF
from groq import Groq


st.set_page_config(page_title="AI SOP Generator", layout="wide")


SVG_CODE = """
<svg xmlns="http://w3.org/2000/svg" viewBox="0 0 240 80" width="240" height="80">
  <rect x="0" y="0" width="240" height="80" fill="#ffffff" rx="12" ry="12"/>
  <g transform="translate(20,40)">
    <circle cx="0" cy="0" r="24" fill="#0A74DA"/>
    <circle cx="8" cy="-6" r="12" fill="#ffffff"/>
  </g>
  <text x="70" y="48" font-family="Arial" font-size="36" font-weight="600" fill="#222222">SOP</text>
  <text x="70" y="70" font-family="Arial" font-size="14" fill="#555555">AI Generator</text>
</svg>
""".strip()


def render_svg_data_uri(svg: str) -> str:
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def create_pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    clean_text = (text or "").encode("latin-1", "ignore").decode("latin-1")
    pdf.multi_cell(0, 6, clean_text)

    return pdf.output() 



def get_groq_api_key() -> str | None:
    try:
        secret = st.secrets.get("GROQ_API_KEY")
        if secret:
            return secret
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY") or None


def build_prompt(topic: str, notes: str) -> str:
    return f"""
Write a clear, professional Standard Operating Procedure (SOP) for the topic below.
Use headings and numbered steps. Include: Purpose, Scope, Definitions (if needed),
Responsibilities, Procedure, Records/Documentation, Safety/Compliance (if relevant),
and a short checklist at the end.

Topic: {topic}
Notes / raw input (may be messy): {notes}
""".strip()


logo_url = render_svg_data_uri(SVG_CODE)

with st.sidebar:
    st.image(logo_url, width=160)
    st.markdown("### How to use")
    st.info(
        "1. Enter a clear **Topic**.\n"
        "2. Paste **raw notes** or a transcript.\n"
        "3. Click **Generate SOP**.\n"
        "4. Download as PDF if needed."
    )

    st.markdown("### Settings")
    temperature = st.slider("Creativity level", 0.0, 1.0, 0.7, 0.05)
    model="llama-3.1-8b-instant"

header_left, header_right = st.columns([1, 6])
with header_left:
    st.image(logo_url, width=70)
with header_right:
    st.title("Professional SOP Generator")
    st.caption("Powered by Groq")

topic = st.text_input("SOP topic", placeholder="e.g., Data Security Protocol")
notes = st.text_area("Input notes / raw text", height=220, placeholder="Paste your notes here...")

api_key = get_groq_api_key()
if not api_key:
    st.warning("Set `GROQ_API_KEY` in Streamlit secrets or as an environment variable to generate SOPs.")

generate = st.button("Generate SOP", type="primary", disabled=not api_key)

if generate:
    if not topic.strip():
        st.error("Please enter an SOP topic.")
    else:
        client = Groq(api_key=api_key)
        with st.spinner("Writing SOP..."):
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional technical writer."},
                        {"role": "user", "content": build_prompt(topic, notes)},
                    ],
                    temperature=float(temperature),
                )
                sop_text = completion.choices[0].message.content or ""
            except Exception as e:
                st.error(f"Generation failed: {e}")
                sop_text = ""

        if sop_text:
            st.subheader("Generated SOP")
            st.markdown(sop_text)

            pdf_bytes = create_pdf_bytes(sop_text)
            safe_name = "".join(c for c in topic.strip() if c.isalnum() or c in (" ", "-", "_")).strip() or "sop"
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"{safe_name}.pdf",
                mime="application/pdf",
            )
