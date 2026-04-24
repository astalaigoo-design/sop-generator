import streamlit as st
import google.generativeai as genai
with st.sidebar:
    st.title("How to use")
    st.info("""
    1. Enter a clear **Topic**.
    2. Paste any **raw notes** or transcripts.
    3. Click **Generate SOP**.
    4. Copy the result into your document!
    """)
    st.markdown("---") 
    
    if st.button("Generate SOP"):   
        
        if topic or raw_notes:    
            with st.spinner("Processing..."):        
                try: 
                
                 model = genai.GenerativeModel('gemini-2.0-flash')
                 response = model.generate_content(f"Create an SOP for {topic}. Notes: {raw_notes}")
                
                # 1. Store the text so we can use it multiple times
                 sop_text = response.text

                 st.subheader("Generated SOP")
                
                # 2. Display with "Copy" icon (using st.code)
                 st.code(sop_text, language="markdown")

                # 3. Add the Download Button
                 st.download_button(
                    label="📥 Download SOP as Text File",
                    data=sop_text,
                    file_name=f"{topic.replace(' ', '_')}_SOP.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.write("Using Model: **Gemini 2.0 Flash**")

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
    # Change from 1.5 to 2.5 or 3.0
    model = genai.GenerativeModel('gemini-2.5-flash') 
    # Alternative for speed: 'gemini-3-flash'
    prompt = f"Convert this transcript into a professional SOP with sections: Title, Goal, Steps, and Troubleshooting:\n\n{raw_text}"
    

   
import os
import google.generativeai as genai
import streamlit as st

# 1. Setup
st.title("SOP Generator")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 2. Inputs
topic = st.text_input("Enter SOP Topic", placeholder="How to clean a printer")
raw_notes = st.text_area("Paste notes here")

# 3. Action
if st.button("Generate SOP"):
    if topic or raw_notes:
        with st.spinner("Processing..."):
            try:
                # Combine inputs for the AI
                full_prompt = f"Create a formal SOP for {topic}. Notes: {raw_notes}"
                
                # Using the confirmed working model
                model = genai.GenerativeModel('gemini-1.5-flash-8b')      
                response = model.generate_content(full_prompt)
                
                # Display result
                st.subheader("Generated SOP")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    else:
        st.warning("Please provide a topic or some notes first!")

