import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI SOP Generator", layout="wide")
st.title("⚡ SOP Generator")

# Simplified API Setup for Local Testing
api_key = st.sidebar.text_input("Enter Google API Key", type="password")

if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to start.")
    st.info("You can get a free key at: https://google.com")
    st.stop()

genai.configure(api_key=api_key)

def generate_sop(raw_text):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Convert this transcript into a professional SOP with sections: Title, Goal, Steps, and Troubleshooting:\n\n{raw_text}"
    

     import os, json, google.generativeai as genai

# 1. Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. The Refined Prompt
prompt = """
Write a professional Standard Operating Procedure (SOP) for: [INSERT TOPIC HERE].

Please follow this exact structure:
1.  **Title**: Bold and clear.
2.  **Scope**: Who is this for and when should it be done?
3.  **Prerequisites**: Tools or supplies needed.
4.  **Safety Warnings**: Highlight any risks.
5.  **Step-by-Step Instructions**: Use numbered lists with action verbs.
6.  **Verification**: How to check if it's done right.

Format with bold headers and bullet points.
"""

# 3. Use the working model (2.0 or 2.5)
model = genai.GenerativeModel("gemini-2.0-flash")

# 4. Generate and Print
response = model.generate_content(prompt)
print(response.text)


# UI
raw_input = st.text_area("Paste notes or transcript here:", height=300)
if st.button("Generate SOP ✨"):
    if raw_input:
        with st.spinner("Engineering your SOP..."):
            result = generate_sop(raw_input)
            st.markdown(result)
    else:
        st.error("Please paste some text first!")

