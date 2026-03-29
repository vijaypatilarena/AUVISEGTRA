import streamlit as st
import os
import tempfile
import hashlib
from pipeline.trailer import TrailerIntelligence
from pipeline.audio import AudioProcessor


def render_trailer_tab():
    # Section header
    st.markdown("""
    <div class="fade-in" style="margin-bottom: 1.5rem;">
        <h2 style="margin-bottom: 0.25rem;">🎬 Trailer Intelligence System</h2>
        <p style="color: var(--text-muted, #64748b); font-size: 0.9rem; margin: 0;">
            Analyze any movie trailer with multimodal AI — genre prediction, storyline inference, and audio-visual metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize component
    groq_key = st.sidebar.text_input(
        "🔑 Groq API Key",
        type="password",
        help="Enter Groq API Key for full LLM analysis (optional)"
    )
    trailer_intel = TrailerIntelligence(groq_api_key=groq_key)
    audio_proc = AudioProcessor()

    # ── Input Section ──
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, rgba(99,102,241,0.06) 0%, rgba(139,92,246,0.03) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <h3 style="margin-top: 0; font-size: 1.1rem;">🔗 Input & Configuration</h3>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_config = st.columns([2, 1])

    with col_input:
        yt_url = st.text_input(
            "YouTube Trailer URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube trailer link"
        )

    with col_config:
        language = st.selectbox(
            "🌐 Output Language",
            ["English", "Hindi", "Spanish", "French", "German", "Japanese", "Korean"],
            help="Language for the generated intelligence report"
        )

    if yt_url:
        st.video(yt_url)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🧠 Generate Intelligence", type="primary", use_container_width=True):
            with st.status("🔄 Analyzing Trailer...", expanded=True):
                # Step 1: Download
                st.write("📥 Downloading trailer...")
                tmp_dir = tempfile.gettempdir()
                video_path, metadata = trailer_intel.download_trailer(yt_url, tmp_dir)
                
                # Show video title if available
                if metadata and 'title' in metadata:
                    st.write(f"🎞️ Analyzing: **{metadata['title']}**")

                # Step 2: Audio/Transcription
                st.write("🎙️ Processing speech...")
                audio_path = os.path.join(tmp_dir, f"trailer_audio_{hashlib.md5(yt_url.encode()).hexdigest()[:10]}.mp3")
                audio_proc.extract_audio(video_path, audio_path)

                transcript = ""
                if groq_key:
                    transcript = trailer_intel.get_transcript(audio_path)
                else:
                    st.warning("⚠️ No API Key in Sidebar — Model will use Mocked Results")
                    transcript = "Transcript unavailable."

                # Step 3: Visual/Audio Features
                st.write("📊 Extracting visual & audio metadata...")
                vis_features = trailer_intel.extract_visual_features(video_path)
                audio_features = audio_proc.extract_mfcc_intensity(audio_path)

                # Step 4: Multi-modal Analysis
                st.write("🧠 Generating multimodal insights (LLM)...")
                scene_desc = (
                    f"Overall visual intensity: {vis_features['mean_intensity']:.2f}, "
                    f"Number of scenes detected: {vis_features['num_scenes']}, "
                    f"Estimated characters in frame: {vis_features['max_characters']}, "
                    f"Visual Complexity: {vis_features['complexity']}"
                )
                results = trailer_intel.analyze_trailer(transcript, scene_desc, metadata, language)

                st.session_state['trailer_results'] = {
                    "analysis": results,
                    "intensity": vis_features['mean_intensity'],
                    "audio_peak": audio_features['intensity'],
                    "language": language
                }
                st.success("✨ Analysis complete!")

    # ── Results Dashboard ──
    st.markdown("---")

    if 'trailer_results' not in st.session_state:
        st.markdown("""
        <div class="fade-in" style="
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(145deg, rgba(99,102,241,0.04) 0%, rgba(139,92,246,0.02) 100%);
            border: 1px dashed rgba(99,102,241,0.2);
            border-radius: 16px;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎬</div>
            <h3 style="margin: 0 0 0.5rem;">No Report Generated</h3>
            <p style="color: var(--text-muted, #64748b); margin: 0;">
                Input a YouTube trailer URL and click Generate to receive a full intelligence report.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        res = st.session_state['trailer_results']
        analysis = res['analysis']
        lang = res.get('language', 'English')

        # ── Report Header ──
        st.markdown("""
        <div class="fade-in">
            <h3>📋 Intelligence Report</h3>
        </div>
        """, unsafe_allow_html=True)

        # ── Genre & Confidence ──
        genre_col, conf_col = st.columns([2, 1])
        with genre_col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, rgba(99,102,241,0.08) 0%, rgba(236,72,153,0.06) 100%);
                border: 1px solid rgba(99,102,241,0.2);
                border-radius: 16px;
                padding: 1.5rem;
            ">
                <p style="color: var(--text-muted, #64748b); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 0.5rem;">Predicted Genre</p>
                <h2 style="margin: 0; font-size: 1.6rem;">{analysis.get('genre', 'Unknown')}</h2>
            </div>
            """, unsafe_allow_html=True)
        with conf_col:
            confidence = float(analysis.get('confidence', 0.9))
            st.metric("🎯 Confidence", f"{confidence:.0%}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Audio-Visual Metrics ──
        st.markdown("""
        <div class="fade-in">
            <h3>📊 Audio-Visual Metrics</h3>
        </div>
        """, unsafe_allow_html=True)

        av1, av2, av3 = st.columns(3)
        av1.metric("☀️ Visual Brightness", f"{res['intensity']:.1f}")
        av2.metric("🔊 Audio Energy", f"{res['audio_peak']:.3f}", delta="+1.2 Thrill Factor")
        av3.metric("🌐 Output Language", lang)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Summary & Storyline ──
        sum_col, story_col = st.columns([1, 1])

        with sum_col:
            st.markdown("""
            <div class="fade-in">
                <h3>📝 Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            with st.container(border=True):
                st.write(analysis.get('summary', 'No summary generated.'))

        with story_col:
            st.markdown("""
            <div class="fade-in">
                <h3>🗺️ Narrative Arc</h3>
            </div>
            """, unsafe_allow_html=True)
            with st.container(border=True):
                st.info(analysis.get('storyline', 'Storyline prediction unavailable.'))

        # ── Language Badge ──
        st.markdown(f"""
        <div style="
            text-align: center;
            margin-top: 1.5rem;
            padding: 0.75rem;
            background: rgba(99,102,241,0.06);
            border-radius: 12px;
            border: 1px solid rgba(99,102,241,0.12);
        ">
            <span style="color: var(--text-muted, #64748b); font-size: 0.8rem;">
                🌍 Detected Language: <strong>Auto</strong> &nbsp;•&nbsp; Output Language: <strong>{lang}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)
