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
    import google.generativeai as genai
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Convert this transcript into a professional SOP with sections: Title, Goal, Steps, and Troubleshooting:\n\n{raw_text}"
    

    import os, json, google.generativeai as genai
# 1. Setupimport os
import google.generativeai as genai
import streamlit as st

# Configure the API key using the environment variable
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


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

# 1. Setup the Model (Keep this)
model = genai.GenerativeModel("gemini-2.0-flash")

topic = st.text_input("Enter SOP Topic (e.g., How to clean a printer)")

# This button is the "Shield" that stops the rate limit errors
if st.button("Generate SOP"):
    if topic:
        try:
            with st.spinner("Writing... please wait."):
                response = model.generate_content(f"Write a professional SOP for: {topic}")
                st.markdown(response.text)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                st.error("Too many requests! Wait 60 seconds and try again.")
            else:
                st.error(f"Error: {e}")
    else:
        st.warning("Please type a topic first!")


# UI
raw_input = st.text_area("Paste notes or transcript here:", height=300)
if st.button("Generate SOP ✨"):
    if raw_input:
        with st.spinner("Engineering your SOP..."):
            result = generate_sop(raw_input)
            st.markdown(result)
    else:
        st.error("Please paste some text first!")

