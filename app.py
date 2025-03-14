import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import defaultdict
from google.generativeai import GenerativeModel

# Configure Gemini
model = GenerativeModel("gemini-2.0-flash")

# Custom CSS for beautiful UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background-color: #F5F7FB;
    }
    
    .stTextInput input {
        border-radius: 15px !important;
        padding: 12px 20px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .speaker-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .speaker-card:hover {
        transform: translateY(-3px);
    }
    
    .header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        border-radius: 0 0 20px 20px;
    }
    
    .processing-animation {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        margin: 2rem 0;
    }
    
    .download-btn {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Beautiful Header Section
st.markdown("""
    <div class="header">
        <h1 style="margin:0;font-weight:700;">📋 MeetingMind AI</h1>
        <p style="margin:0;opacity:0.9;">Visualize and analyze meeting transcripts with powerful insights</p>
    </div>
""", unsafe_allow_html=True)

# File Uploader
uploaded_file = st.file_uploader("📄 Upload Meeting Transcript", type=["txt"])

if uploaded_file:
    try:
        # Read the transcript
        transcript = uploaded_file.read().decode("utf-8")
        
        # Parse the transcript
        speaker_data = defaultdict(list)
        lines = transcript.split("\n")
        
        for line in lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                speaker = speaker.strip()
                text = text.strip()
                speaker_data[speaker].append(text)
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([(speaker, len(texts)) for speaker, texts in speaker_data.items()], 
                          columns=["Speaker", "Word Count"])
        
        # Visualizations
        st.subheader("📊 Meeting Insights")
        
        # Speaker Contribution Chart
        st.markdown("### Speaker Contribution")
        fig, ax = plt.subplots()
        df.set_index("Speaker")["Word Count"].plot(kind="bar", ax=ax, color="#6366F1")
        ax.set_ylabel("Word Count")
        ax.set_xlabel("Speaker")
        st.pyplot(fig)
        
        # Word Cloud (Optional)
        st.markdown("### Word Cloud")
        st.write("Coming soon! (Enable with `wordcloud` library)")
        
        # Sentiment Analysis (Optional)
        st.markdown("### Sentiment Analysis")
        st.write("Coming soon! (Enable with `textblob` or `vaderSentiment`)")
        
        # Speaker Summaries
        st.subheader("🗣️ Speaker Summaries")
        for speaker, texts in speaker_data.items():
            response = model.generate_content(f"Summarize the following points in bullet format:\n{''.join(texts)}")
            
            st.markdown(f"""
                <div class="speaker-card">
                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <div style="background: #6366F1; width: 40px; height: 40px; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; color: white;
                            font-weight: 600; margin-right: 1rem;">
                            {speaker[0].upper()}
                        </div>
                        <h3 style="margin:0;color:#1F2937">{speaker}</h3>
                    </div>
                    <div style="color:#4B5563;line-height:1.6">{response.text}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Download Section
        st.markdown("---")
        col1, col2 = st.columns([2,1])
        with col1:
            st.subheader("📥 Export Results")
            st.markdown("""
                Export your meeting analysis in a professional format suitable for sharing with stakeholders.
            """)
        with col2:
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            minutes_file = "meeting_analysis.txt"
            with open(minutes_file, "w") as f:
                f.write("Meeting Analysis Report\n\n")
                f.write("Speaker Contributions:\n")
                f.write(df.to_string(index=False) + "\n\n")
                f.write("Speaker Summaries:\n")
                for speaker, texts in speaker_data.items():
                    f.write(f"{speaker}:\n{'- ' + '\n- '.join(texts)}\n\n")
            
            st.download_button("Download Full Report", 
                             data=open(minutes_file, "rb"), 
                             file_name="meeting_analysis.txt",
                             mime="text/plain",
                             use_container_width=True,
                             type="primary")
    
    except Exception as e:
        st.error(f"🚨 Error: {e}")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 4rem; color: #6B7280; font-size: 0.9rem;">
        <hr style="border: 0.5px solid #E5E7EB; margin-bottom: 1rem;">
        Powered by Gemini AI • MeetingMind 2024 • v1.3.0
    </div>
""", unsafe_allow_html=True)