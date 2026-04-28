import os


import streamlit as st
import base64
from io import BytesIO
from fpdf import FPDF
from groq import Groq
from docx import Document


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

def create_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # Clean the text
    clean_text = (text or "").encode("latin-1", "ignore").decode("latin-1")
    pdf.multi_cell(0, 10, txt=clean_text)
    
    out = pdf.output(dest="S")
    # fpdf (PyFPDF) may return `str`, while fpdf2 often returns `bytes`/`bytearray`.
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)


def create_docx_bytes(title: str, text: str) -> bytes:
    doc = Document()
    if title.strip():
        doc.add_heading(title.strip(), level=1)

    for raw_line in (text or "").splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
        else:
            doc.add_paragraph(line)

    buff = BytesIO()
    doc.save(buff)
    return buff.getvalue()




def get_groq_api_key() -> str | None:
    try:
        secret = st.secrets.get("GROQ_API_KEY")
        if secret:
            return secret
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY") or None


TEMPLATE_GUIDANCE: dict[str, str] = {
    "IT SOP": """
Focus on technical accuracy, security, and repeatability.
Include: Preconditions/requirements, access/permissions, tools/systems involved,
rollback plan, troubleshooting, validation steps, logging/monitoring, and SLAs/owners.
Add a short 'Change management' section (impact, approvals, maintenance window).
""".strip(),
    "HR SOP": """
Focus on compliance, privacy, fairness, and a clear human workflow.
Include: Trigger events, required forms/documents, approvals, timelines/SLAs,
confidentiality/data handling, escalation paths, templates/communications, and record retention.
Add a short 'Candidate/employee communication' checklist.
""".strip(),
    "Warehouse SOP": """
Focus on safety, efficiency, and physical process clarity.
Include: PPE/safety requirements, equipment/tools, location/bin labeling, scanning steps,
quality checks, exception handling (damages/shortages), and end-of-shift reconciliation.
Add a short 'Safety checks' section and 'Common errors to avoid'.
""".strip(),
    "Restaurant SOP": """
Focus on food safety, service consistency, and speed.
Include: food safety controls (temps, cross-contamination), prep/line setup,
service steps, cleaning schedules, allergen handling, customer escalation, and close-down tasks.
Add checklists for opening/shift/closing and 'Quality standards' (taste, plating, timing).
""".strip(),
}


def build_prompt_for_template(
    template_name: str,
    topic: str,
    notes: str,
    *,
    audience: str,
    tools_used: str,
    compliance_standard: str,
    strictness: str,
    include_definitions: bool,
    include_safety_compliance: bool,
    include_records: bool,
    include_checklist: bool,
) -> str:
    template_guidance = TEMPLATE_GUIDANCE.get(template_name, "")

    strictness_instructions = (
        "Strictness: STRICT. Use a formal, policy-like tone. Use short, unambiguous steps. "
        "Avoid fluff. Prefer MUST/SHALL where appropriate. Include clear acceptance/verification criteria."
        if strictness == "Strict"
        else "Strictness: DETAILED. Be thorough and explanatory while staying professional. "
        "Include tips, examples, and clarifying notes where helpful."
    )

    section_lines = [
        "- Purpose",
        "- Scope",
        "- Roles & responsibilities",
        "- Procedure (numbered)",
        "- Exceptions / edge cases",
    ]
    if include_definitions:
        section_lines.append("- Definitions (only if needed)")
    if include_records:
        section_lines.append("- Records / documentation")
    if include_safety_compliance:
        section_lines.append("- Safety / compliance (if relevant)")
    if include_checklist:
        section_lines.append("- Checklist (short, at the end)")

    sections_text = "\n".join(section_lines)
    return f"""
Write a clear, professional Standard Operating Procedure (SOP) for the topic below.
Use crisp headings and numbered steps. Keep it practical and immediately actionable.

Target audience: {audience}
Tools/systems used: {tools_used or "Not specified"}
Compliance standard(s): {compliance_standard or "Not specified"}
{strictness_instructions}

Required sections (include ONLY these; omit all others):
{sections_text}

Template-specific guidance:
{template_guidance}

Topic: {topic}
Notes / raw input (may be messy): {notes}
""".strip()


@st.cache_data(show_spinner=False, ttl=3600, max_entries=256)
def generate_sop_cached(
    *,
    api_key: str,
    model: str,
    temperature: float,
    prompt: str,
) -> str:
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional technical writer."},
            {"role": "user", "content": prompt},
        ],
        temperature=float(temperature),
    )
    return completion.choices[0].message.content or ""


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
    template_name = st.selectbox(
        "Template",
        ["IT SOP", "HR SOP", "Warehouse SOP", "Restaurant SOP"],
        index=0,
    )

    strictness = st.radio("Strictness", ["Strict", "Detailed"], index=1, horizontal=True)

    audience = st.text_input(
        "Audience (optional)",
        placeholder="e.g., New hires, IT admins, Shift supervisors",
    )
    tools_used = st.text_input(
        "Tools used (optional)",
        placeholder="e.g., Okta, Jira, Google Workspace, Forklifts, POS system",
    )
    compliance_standard = st.selectbox(
        "Compliance standard (optional)",
        ["None", "ISO 27001", "SOC 2", "HIPAA"],
        index=0,
    )
    compliance_standard = "" if compliance_standard == "None" else compliance_standard

    st.markdown("### Outline controls")
    include_definitions = st.checkbox("Include Definitions section", value=True)
    include_safety_compliance = st.checkbox("Include Safety/Compliance section", value=True)
    include_records = st.checkbox("Include Records/Documentation section", value=True)
    include_checklist = st.checkbox("Include Checklist section", value=True)

    temperature = st.slider("Creativity level", 0.0, 1.0, 0.7, 0.05)
    model="llama-3.1-8b-instant"

    if st.button("Clear cached results"):
        st.cache_data.clear()


header_left, header_right = st.columns([1, 6])
with header_left:
    st.image(logo_url, width=70)
with header_right:
    st.title("Professional SOP Generator")
    st.caption("Powered by Groq")

notes = st.text_area("Input notes / raw text", height=220, placeholder="Paste your notes here...")

api_key = get_groq_api_key()
if not api_key:
    st.warning("Set `GROQ_API_KEY` in Streamlit secrets or as an environment variable to generate SOPs.")

generate = st.button("Generate SOP", type="primary", disabled=not api_key)

if generate:
    if not notes.strip():
        st.error("Please paste your notes (or a transcript) first.")
    else:
        with st.spinner("Writing SOP..."):
            try:
                inferred_topic = f"{template_name} SOP"
                prompt = build_prompt_for_template(
                    template_name,
                    inferred_topic,
                    notes,
                    audience=audience.strip() or "General staff",
                    tools_used=tools_used.strip(),
                    compliance_standard=compliance_standard.strip(),
                    strictness=strictness,
                    include_definitions=include_definitions,
                    include_safety_compliance=include_safety_compliance,
                    include_records=include_records,
                    include_checklist=include_checklist,
                )
                sop_text = generate_sop_cached(
                    api_key=api_key,
                    model=model,
                    temperature=float(temperature),
                    prompt=prompt,
                )
            except Exception as e:
                st.error(f"Generation failed: {e}")
                sop_text = ""

        if sop_text:
            st.subheader("Generated SOP")
            st.markdown(sop_text)

            pdf_bytes = create_pdf_bytes(sop_text)
            safe_name = "".join(c for c in inferred_topic.strip() if c.isalnum() or c in (" ", "-", "_")).strip() or "sop"
            docx_bytes = create_docx_bytes(safe_name, sop_text)

            col_a, col_b = st.columns(2)
            with col_a:
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"{safe_name}.pdf",
                    mime="application/pdf",
                )
            with col_b:
                st.download_button(
                    "Download DOCX",
                    data=docx_bytes,
                    file_name=f"{safe_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
