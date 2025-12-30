import streamlit as st
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.groq_service import get_groq_service

st.title("Grammar Check")
st.write("Improve your writing with our AI-powered grammar checker")

# Initialize Groq service
@st.cache_resource
def init_groq_service():
    try:
        return get_groq_service()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None

groq_service = init_groq_service()

user_text = st.text_area("Enter your text here:", height=150)

def check_grammar(text):
    """Check grammar using Groq API directly"""
    if groq_service is None:
        return {"error": "Groq service not initialized. Please check your API key."}
    
    return groq_service.check_grammar(text)


if st.button("Find Grammatical Mistakes"):
    if user_text:
        with st.spinner("Checking grammar..."):
            fixed_grammar = check_grammar(user_text)

            if "error" in fixed_grammar:
                st.error(f"Error: {fixed_grammar['error']}")
            else:
                st.subheader("Results:")

                # Original vs Corrected Text
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Original Text")
                    st.info(fixed_grammar["original_text"])
                
                with col2:
                    st.markdown("### Corrected Text")
                    st.success(fixed_grammar["corrected_text"])
                
                # Display corrections
                if fixed_grammar["corrections"]:
                    st.markdown("### Corrections")
                    
                    for i, correction in enumerate(fixed_grammar["corrections"]):
                        with st.expander(f"Correction {i+1}: {correction.get('type', 'Unknown').title()}"):
                            cols = st.columns([1, 1])
                            with cols[0]:
                                st.markdown("**Error:**")
                                st.markdown(f"<span style='color:red'>{correction.get('error', 'N/A')}</span>", unsafe_allow_html=True)
                            
                            with cols[1]:
                                st.markdown("**Suggestion:**")
                                st.markdown(f"<span style='color:green'>{correction.get('suggestion', 'N/A')}</span>", unsafe_allow_html=True)
                            
                            st.markdown("**Explanation:**")
                            st.markdown(f"_{correction.get('explanation', 'No explanation provided')}_")
                            
                            # Add Grammar Rule section if available
                            if 'grammar_rule' in correction and correction['grammar_rule']:
                                st.markdown("**Grammar Rule:**")
                                rule = correction['grammar_rule']
                                st.markdown(f"**{rule.get('rule_name', 'Rule')}**")
                                st.markdown(rule.get('description', ''))
                                
                                # Display correct examples
                                if rule.get('correct_examples'):
                                    st.markdown("**Correct Examples:**")
                                    for example in rule['correct_examples']:
                                        st.markdown(f"- ✅ *{example}*")
                                
                                # Display incorrect examples
                                if rule.get('incorrect_examples'):
                                    st.markdown("**Incorrect Examples:**")
                                    for example in rule['incorrect_examples']:
                                        st.markdown(f"- ❌ *{example}*")
                            
                    # Summary
                    st.success(f"Found {len(fixed_grammar['corrections'])} grammar issues to fix.")
                else:
                    st.success("No grammar issues found. Your text looks good!")
                
                # Add a download button for the corrected text
                st.download_button(
                    label="Download Corrected Text",
                    data=fixed_grammar["corrected_text"],
                    file_name="corrected_text.txt",
                    mime="text/plain"
                )
    else:
        st.warning("Please enter some text to check.")

# Add a footer
st.markdown("""
---
*Powered by Groq AI - Llama 3.3 70B*
""")
