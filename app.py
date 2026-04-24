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
    
    try:
        # We add 'stream=False' to force a standard connection
        response = model.generate_content(prompt, stream=False)
        return response.text
    except Exception as e:
        return f"System Message: {str(e)}"

# UI
raw_input = st.text_area("Paste notes or transcript here:", height=300)
if st.button("Generate SOP ✨"):
    if raw_input:
        with st.spinner("Engineering your SOP..."):
            result = generate_sop(raw_input)
            st.markdown(result)
    else:
        st.error("Please paste some text first!")

