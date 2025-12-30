import streamlit as st
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.groq_service import get_groq_service

# Initialize Groq service
@st.cache_resource
def init_groq_service():
    try:
        return get_groq_service()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None

groq_service = init_groq_service()


def plagiarism_checker_page():
    st.title("Plagiarism Checker")
    st.write("Check your content for plagiarism with our AI-powered tool.")
    
    # Add tabs for text input and file upload
    tab1, tab2 = st.tabs(["Text Input", "File Upload"])
    
    with tab1:
        text_to_check = st.text_area("Paste the content you want to check for plagiarism:", height=200)
    
    with tab2:
        uploaded_file = st.file_uploader("Upload a .txt or .docx file", type=["txt", "docx"])
        if uploaded_file is not None:
            # Handle different file types
            if uploaded_file.name.endswith('.txt'):
                text_to_check = uploaded_file.read().decode("utf-8")
                st.success(f"File '{uploaded_file.name}' loaded successfully!")
            elif uploaded_file.name.endswith('.docx'):
                try:
                    import docx
                    doc = docx.Document(uploaded_file)
                    text_to_check = "\n".join([para.text for para in doc.paragraphs])
                    st.success(f"File '{uploaded_file.name}' loaded successfully!")
                except Exception as e:
                    st.error(f"Error reading .docx file: {str(e)}")
                    st.info("Please make sure you have the python-docx package installed.")
                    text_to_check = ""
    
    if st.button("Check for Plagiarism"):
        if 'text_to_check' in locals() and text_to_check:
            with st.spinner("Analyzing text for potential plagiarism..."):
                # Call the plagiarism checking function directly
                result = check_plagiarism(text_to_check)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Display the results
                    display_plagiarism_results(result, text_to_check)
        else:
            st.warning("Please enter some text or upload a file to check for plagiarism.")

def check_plagiarism(text):
    """Check plagiarism using Groq API directly"""
    if groq_service is None:
        return {"error": "Groq service not initialized. Please check your API key."}
    
    return groq_service.check_plagiarism(text)

def display_plagiarism_results(result, original_text):
    """Display the plagiarism check results in a user-friendly way"""
    score = result.get("plagiarism_score", 0)
    flagged = result.get("flagged_sentences", [])
    feedback = result.get("feedback", "")

    st.markdown(f"### Plagiarism Score: {score}/100")
    if score > 50:
        st.error(f"High likelihood of plagiarism/AI generation.")
    elif score > 20:
        st.warning(f"Some potential issues detected.")
    else:
        st.success("Content appears original.")

    st.markdown("### Feedback")
    st.info(feedback)

    if flagged:
        st.markdown("### Flagged Sentences")
        for sentence in flagged:
            st.warning(f"- {sentence}")

if __name__ == "__main__":
    plagiarism_checker_page()