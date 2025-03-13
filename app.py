import streamlit as st
import yt_dlp
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
        <p style="margin:0;opacity:0.9;">Transform video meetings into organized minutes with speaker identification</p>
    </div>
""", unsafe_allow_html=True)

# Main Content
with st.container():
    col1, col2 = st.columns([3,1])
    with col1:
        video_url = st.text_input(" ", placeholder="🎥 Paste meeting video URL here...")
    with col2:
        st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
        st.button("ℹ️ How it works")

if video_url:
    try:
        # Processing Status
        with st.status("🔍 Analyzing your meeting content...", expanded=True) as status:
            # Audio Extraction
            st.write("📡 Connecting to video source...")
            ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                audio_url = info.get('url', None)
            
            if not audio_url:
                st.error("❌ Failed to retrieve audio stream")
                st.stop()
            
            # Transcription
            st.write("🎙️ Transcribing audio...")
            transcript_response = model.generate_content(f"Transcribe the following audio: {audio_url}")
            full_transcript = transcript_response.text
            
            # Speaker Identification
            st.write("👥 Identifying speakers...")
            name_prompt = f"""Analyze this meeting transcript and replace generic speaker labels with actual names. 
            Maintain format with 'Name: text'.\n\n{full_transcript}"""
            updated_response = model.generate_content(name_prompt)
            updated_transcript = updated_response.text
            
            # Processing Complete
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        # Results Section
        st.subheader("📊 Meeting Insights")
        
        # Speaker Summaries
        transcript_lines = updated_transcript.split("\n")
        speaker_transcripts = {}
        
        for line in transcript_lines:
            if ":" in line:
                speaker, text = line.split(":", 1)
                speaker = speaker.strip()
                text = text.strip()
                if speaker not in speaker_transcripts:
                    speaker_transcripts[speaker] = []
                speaker_transcripts[speaker].append(text)
        
        # Display Beautiful Cards
        for speaker, texts in speaker_transcripts.items():
            response = model.generate_content("Summarize these points in bullet format:\n" + "\n".join(texts))
            
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
                Export your meeting minutes in a professional format suitable for sharing with stakeholders.
            """)
        with col2:
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            minutes_file = "meeting_minutes.txt"
            with open(minutes_file, "w") as f:
                for speaker, texts in speaker_transcripts.items():
                    f.write(f"{speaker}:\n{'- ' + '\n- '.join(texts)}\n\n")
            
            st.download_button("Download Full Report", 
                             data=open(minutes_file, "rb"), 
                             file_name="meeting_minutes.txt",
                             mime="text/plain",
                             use_container_width=True,
                             type="primary")

        # Full Transcript Accordion
        with st.expander("📜 View Full Transcript", expanded=False):
            st.markdown(f"""
                <div style="background: white; padding: 1.5rem; border-radius: 12px;
                            border: 1px solid #E5E7EB; margin-top: 1rem;">
                    {updated_transcript.replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚨 Error: {e}")

# Footer
st.markdown("""
    <div style="text-align: center; margin-top: 4rem; color: #6B7280; font-size: 0.9rem;">
        <hr style="border: 0.5px solid #E5E7EB; margin-bottom: 1rem;">
        Powered by Gemini AI • MeetingMind 2024 • v1.2.0
    </div>
""", unsafe_allow_html=True)
