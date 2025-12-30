import streamlit as st
import re
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

# --- Helper Functions --- #
def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_transcript(video_id):
    """Get transcript from YouTube video using youtube-transcript-api"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Use list_transcripts to get available transcripts, then fetch
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript first, otherwise get the first available
        try:
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
        except:
            # Get the first available transcript
            transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Combine all transcript parts into one text
        full_transcript = " ".join([item['text'] for item in transcript_data])
        return {"transcript": full_transcript}
    except ImportError:
        return {"error": "youtube-transcript-api is not installed. Please run: pip install youtube-transcript-api"}
    except Exception as e:
        error_msg = str(e)
        if "Could not retrieve" in error_msg or "No transcript" in error_msg or "TranscriptsDisabled" in error_msg:
            return {"error": "No transcript available for this video. The video might not have captions enabled."}
        return {"error": f"Error getting transcript: {error_msg}"}


def summarize_video(video_id):
    """Get transcript and summarize using Groq"""
    if groq_service is None:
        return {"error": "Groq service not initialized. Please check your API key."}
    
    # Get transcript
    transcript_result = get_youtube_transcript(video_id)
    if "error" in transcript_result:
        return transcript_result
    
    # Summarize with Groq
    transcript = transcript_result["transcript"]
    
    # Truncate if too long (Groq has token limits)
    max_chars = 15000  # Roughly 3750 tokens
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "... [transcript truncated]"
    
    return groq_service.summarize_youtube(transcript)

# --- Session State Initialization --- #
if 'summary_history' not in st.session_state:
    st.session_state.summary_history = []

# --- UI Layout --- #
st.set_page_config(page_title="YouTube Summarizer", layout="wide")
st.title("📺 YouTube Video Summarizer")
st.write("Enter a YouTube URL to get an AI-powered summary of the video content!")

# Sidebar for history
st.sidebar.header("Summary History")
if st.session_state.summary_history:
    for i, entry in enumerate(reversed(st.session_state.summary_history)):
        with st.sidebar.expander(f"Video {len(st.session_state.summary_history) - i}"):
            st.markdown(f"**URL:** {entry['url'][:50]}...")
            if 'title' in entry:
                st.markdown(f"**Title:** {entry['title']}")
            st.markdown(f"**Summary:** {entry['summary'][:100]}...")
else:
    st.sidebar.info("No videos summarized yet.")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Enter YouTube URL")
    youtube_url = st.text_input(
        "YouTube URL:", 
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste any YouTube video URL here"
    )
    
    # Validate URL and show preview
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        if video_id:
            st.success("✅ Valid YouTube URL detected!")
            
            # Show video preview
            st.subheader("Video Preview")
        
            
            # Embed video player
            st.video(youtube_url)
            
        else:
            st.error("❌ Invalid YouTube URL. Please enter a valid YouTube video URL.")
            video_id = None
    else:
        video_id = None

with col2:
    st.subheader("Actions")
    
    # Summarize button
    if st.button("🔄 Summarize Video", disabled=not video_id, help="Click to generate AI summary"):
        if video_id:
            with st.spinner("🤖 Analyzing video content... This may take a few minutes."):
                result = summarize_video(video_id)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    # Store in history
                    history_entry = {
                        "url": youtube_url,
                        "video_id": video_id,
                        "summary": result.get("summary", "Summary not available"),
                        "title": result.get("title", "Title not available")
                    }
                    st.session_state.summary_history.append(history_entry)
                    
                    # Display results
                    st.success("✅ Video summarized successfully!")
    
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.summary_history = []
        st.success("History cleared!")

# Display current summary results
if st.session_state.summary_history:
    latest_summary = st.session_state.summary_history[-1]
    
    st.markdown("---")
    st.subheader("📝 Latest Summary")
    
    # Display video title if available
    if 'title' in latest_summary and latest_summary['title'] != "Title not available":
        st.markdown(f"**🎬 Video Title:** {latest_summary['title']}")
    
    # Display summary
    st.markdown("**📋 Summary:**")
    st.info(latest_summary['summary'])
    
    # Display video URL
    st.markdown(f"**🔗 Source:** [Watch Video]({latest_summary['url']})")
