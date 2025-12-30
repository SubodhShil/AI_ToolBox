import streamlit as st
import pandas as pd
import numpy as np

# Initialize session state for model selection (for compatibility with legacy code)
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Llama 3.3 70B"

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,100..900;1,100..900&family=Karla:ital,wght@0,200..800;1,200..800&family=Raleway:ital,wght@0,100..900;1,100..900&family=Sofia+Sans:ital,wght@0,1..1000;1,1..1000&display=swap');

html, body, [class*="css"] {
    font-family: "Raleway", sans-serif;
    font-family: "Karla", sans-serif;
    font-family: "Archivo", sans-serif;
    font-family: "Sofia Sans", sans-serif;
}

.stApp {
    font-family: "Raleway", sans-serif;
    font-family: "Karla", sans-serif;
    font-family: "Archivo", sans-serif;
    font-family: "Sofia Sans", sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Raleway", sans-serif !important;
    font-family: "Karla", sans-serif !important;
    font-family: "Archivo", sans-serif !important;
    font-family: "Sofia Sans", sans-serif !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# Application Title
st.write("# RAG ToolBox")


# Define the gradient_div function first
def gradient_div(content, bg, page_link):
    features_section = f"""
        <a href="{page_link}" target="_self" style="
            height: 70px;
            width: 100%;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 25px;
            display: flex;
            text-align: center;
            flex-direction: column;
            color: white;
            font-size: 18px;
            font-weight: 600;
            background: {bg};
            align-items: center;
            justify-content: center;
            box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
            text-decoration: none;
            transition: all 0.3s ease;
        ">
            {content}
        </a>
        <style> 
            a:hover {{
                transform: translateY(-3px);
                box-shadow: 0px 12px 24px rgba(0,0,0,0.15);
            }}
        </style>
    """
    return features_section


# Animated instruction box
st.markdown(
    """
<div style="
    padding: 20px;
    margin: 20px 0;
    border-radius: 12px;
    background: rgba(30, 30, 40, 0.7);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(100, 149, 237, 0.3);
    text-align: center;
">
    <div style="
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            rgba(30, 30, 40, 0) 0%, 
            rgba(100, 149, 237, 0.3) 50%, 
            rgba(30, 30, 40, 0) 100%);
        animation: shimmer 3s infinite;
        z-index: 0;
    "></div>
    <div style="
        position: relative;
        z-index: 1;
        color: #f0f0f0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    ">
        <h3 style="color: #64b5f6; margin-top: 0; width: 100%; text-align: center;">📚 Welcome to RAG ToolBox! 🎉</h3>
        <p style="margin-bottom: 16px; width: 100%; text-align: center;"> Explore our AI-powered tools below</p>
    </div>
</div>

<style>
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    #emoji::after {
        content: '💡';
        animation: changeEmoji 4s infinite;
    }
    
    @keyframes changeEmoji {
        0% { content: '💡'; }
        20% { content: '✨'; }
        40% { content: '🚀'; }
        60% { content: '🎯'; }
        80% { content: '🔮'; }
        100% { content: '💡'; }
    }
    
    a:hover {
        transform: translateY(-3px);
        box-shadow: 0px 12px 24px rgba(0,0,0,0.15);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Create a 2-column layout
col1, col2 = st.columns(2)

with col2:
    st.markdown(
        gradient_div(
            "Grammar Check",
            "linear-gradient(to right, #4776E6, #8E54E9)",
            "/Grammar_Check",
        ),
        unsafe_allow_html=True,
    )

# Second row
with col1:
    st.markdown(
        gradient_div(
            "Paraphraser", "linear-gradient(to right, #11998e, #38ef7d)", "/Paraphraser"
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        gradient_div(
            "AI Chat", "linear-gradient(to right, #2980B9, #6DD5FA)", "/AI_Chat"
        ),
        unsafe_allow_html=True,
    )


# Fourth row
with col1:
    st.markdown(
        gradient_div(
            "Plagiarism Checker",
            "linear-gradient(to right, #3A1C71, #D76D77)",
            "/Plagiarism_Checker",
        ),
        unsafe_allow_html=True,
    )

with col1:
    st.markdown(
        gradient_div(
            "YouTube Summarizer",
            "linear-gradient(to right, #FF5F6D, #FFC371)",
            "/Youtube_summarizer",
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        gradient_div(
            "Image Watermark Checking",
            "linear-gradient(to right, #11998e, #38ef7d)",
            "/Image_watermark_checking",
        ),
        unsafe_allow_html=True,
    )

# Fifth row has been removed as Document Summarizer page was deleted

# Sidebar
st.sidebar.title("Settings")

# Get all available pages
pages = [
    "Grammar_Check",
    "AI_Chat",
    "Paraphraser",
    "Resume_Maker",
    "Speaking_Assistant",
    "Plagiarism_Checker",
    "Image_watermark_checking",
    "Writing_Challenge",
]

# API Methods section
api_method = st.sidebar.selectbox("### API Methods", ("Freemium", "Your Own API"))


# Function to update the selected model in session state
def update_model(model_name):
    st.session_state.selected_model = model_name
    st.sidebar.success(f"Selected model: {model_name}")


if api_method == "Freemium":
    model = st.sidebar.selectbox("Select Model", ("Llama 3.3 70B", "Llama 3.1 8B", "Mixtral 8x7B"))

    # Update the selected model when it changes
    if st.sidebar.button("Set Model"):
        update_model(model)

    st.sidebar.write(f"Current model: {st.session_state.selected_model}")
    st.sidebar.info("Powered by Groq AI")

else:
    api_input = st.sidebar.text_input(
        "Enter your API key", key="api_input", type="password"
    )

    if st.sidebar.button("Set API Key"):
        st.sidebar.success("API Key set successfully!")

footer = """
<style>

.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    color: #888;
    padding: 10px;
    text-align: right;
    font-size: 14px;
    z-index: 999;
}

</style>

<div class="footer">
    RAG ToolBox | Created with ⚡ by <a href="">Subodh Chandra Shil</a> 
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
