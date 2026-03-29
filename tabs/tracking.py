import streamlit as st
import os
import tempfile
import pandas as pd
import numpy as np
import plotly.express as px
from pipeline.video import find_scenes, get_video_info
from pipeline.tracking import Tracker
from pipeline.reid import PersonReID
from pipeline.audio import AudioProcessor
from pipeline.fusion import FusionEngine


def render_tracking_tab(alpha, beta):
    # Section header
    st.markdown("""
    <div class="fade-in" style="margin-bottom: 1.5rem;">
        <h2 style="margin-bottom: 0.25rem;">🔍 Character Tracking System</h2>
        <p style="color: var(--text-muted, #64748b); font-size: 0.9rem; margin: 0;">
            Upload a video to detect, track, and re-identify characters across scenes using multimodal fusion.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize components
    tracker = Tracker()
    reid = PersonReID()
    
    # ── Sidebar Configuration Extension ──
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔑 Authentication")
        hf_token = st.text_input(
            "Hugging Face Token",
            type="password",
            help="Required for Pyannote Speaker Diarization (pyannote/speaker-diarization@2.1)"
        )
    
    audio_proc = AudioProcessor(hf_token=hf_token if hf_token else None)
    fusion = FusionEngine(alpha, beta)

    if 'tracking_results' not in st.session_state:
        st.session_state['tracking_results'] = None

    # ── Upload Section ──
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, rgba(99,102,241,0.06) 0%, rgba(139,92,246,0.03) 100%);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    ">
        <h3 style="margin-top: 0; font-size: 1.1rem;">📤 Upload & Process</h3>
    </div>
    """, unsafe_allow_html=True)

    col_upload, col_preview = st.columns([1, 1])

    with col_upload:
        video_file = st.file_uploader(
            "Upload a video for processing",
            type=["mp4", "avi", "mov"],
            key="tracking_uploader",
            help="Supported: MP4, AVI, MOV — Max 200MB"
        )

    with col_preview:
        if video_file:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(video_file.read())
            video_path = tfile.name
            st.video(video_path)

    if video_file:
        if st.button("⚡ Process Video", type="primary", use_container_width=True):
            with st.status("🧠 Analyzing Video...", expanded=True):
                # Step 1: Video Info
                info = get_video_info(video_path)
                st.write(f"🎞️ Video Duration: **{info['duration']:.2f}s** | FPS: **{info['fps']}**")

                # Step 2: Scene Detection
                st.write("🔍 Detecting scenes...")
                scenes = find_scenes(video_path)
                st.write(f"✅ Found **{len(scenes)}** scenes.")

                # Step 3: Audio Diarization
                st.write("🎙️ Extracting and diarizing audio...")
                audio_path = os.path.join(tempfile.gettempdir(), f"audio_{os.path.basename(video_path)}.wav")
                audio_proc.extract_audio(video_path, audio_path)
                speaker_segments = audio_proc.diarize_audio(audio_path)
                if not hf_token:
                    st.info("💡 Note: Using mock diarization (HF Token missing).")

                # Step 4: Visual Tracking & ReID
                st.write("🕺 Detecting and identifying characters (Literal YOLO + ReID)...")
                import cv2
                cap = cv2.VideoCapture(video_path)
                person_appearances = []
                
                # Limit to 5 scenes for performance in demo, or process all if short
                scenes_to_process = scenes[:10] 
                
                progress_bar = st.progress(0, text="Analyzing scenes...")
                for i, scene in enumerate(scenes_to_process):
                    start_frame = scene[0].get_frames()
                    end_frame = scene[1].get_frames()
                    
                    # Sample 1 frame from the middle of the scene for ReID
                    middle_frame_idx = (start_frame + end_frame) // 2
                    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Detect persons
                        results = tracker.model(frame, classes=[0], verbose=False)
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        
                        for j, box in enumerate(boxes):
                            # Extract crop
                            x1, y1, x2, y2 = map(int, box)
                            crop = frame[y1:y2, x1:x2]
                            if crop.size > 0:
                                crop_path = os.path.join(tempfile.gettempdir(), f"p_s{i}_f{middle_frame_idx}_c{j}.jpg")
                                cv2.imwrite(crop_path, crop)
                                
                                # Extract ReID features
                                visual_emb = reid.extract_features(crop_path)
                                
                                person_appearances.append({
                                    "scene_id": i,
                                    "start": start_frame / info['fps'],
                                    "end": end_frame / info['fps'],
                                    "visual_embedding": visual_emb,
                                    "thumbnail": crop_path
                                })
                    
                    progress_bar.progress((i + 1) / len(scenes_to_process), text=f"Processed scene {i+1}/{len(scenes_to_process)}")
                
                cap.release()

                # Step 5: Multimodal Fusion
                st.write("🔗 Performing Multimodal Fusion...")
                if person_appearances:
                    # Align visuals with speaker segments
                    aligned_data = fusion.align_audio_visual(person_appearances, speaker_segments)
                    # Cluster all segments into global identities
                    final_data = fusion.cluster_identities(aligned_data)
                    
                    # Aggregate results for dashboard
                    dashboard_results = format_literal_results(final_data, len(scenes), info['duration'])
                    st.session_state['tracking_results'] = dashboard_results
                    st.success("✨ Literal analysis complete!")
                else:
                    st.warning("⚠️ No characters detected in the sampled scenes.")

    # ── Results Dashboard ──
    st.markdown("---")
    results = st.session_state['tracking_results']

    if results is None:
        st.markdown("""
        <div class="fade-in" style="
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(145deg, rgba(99,102,241,0.04) 0%, rgba(139,92,246,0.02) 100%);
            border: 1px dashed rgba(99,102,241,0.2);
            border-radius: 16px;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎬</div>
            <h3 style="margin: 0 0 0.5rem;">No Results Yet</h3>
            <p style="color: var(--text-muted, #64748b); margin: 0;">
                Upload and process a video to see multimodal character intelligence.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Metric Cards Row ──
        st.markdown("""
        <div class="fade-in">
            <h3>📊 Intelligence Overview</h3>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🎭 Unique Characters", f"{len(results['characters'])}")
        m2.metric("🎬 Total Scenes", f"{results['total_scenes']}")
        m3.metric("📊 Processed Segments", f"{results['num_segments']}")
        m4.metric("🎙️ Voice Diarization", "Enabled" if hf_token else "Mocked")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Character Breakdown Table ──
        st.markdown("""
        <div class="fade-in">
            <h3>🎭 Character Breakdown</h3>
        </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(results['characters'])
        if not df.empty:
            st.dataframe(
                df.drop(columns=['thumbnail']),
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts Row ──
        chart_col1, chart_col2 = st.columns([1, 1])

        with chart_col1:
            st.markdown("""
            <div class="fade-in">
                <h3>🗺️ Appearance Heatmap</h3>
            </div>
            """, unsafe_allow_html=True)

            heatmap_data = results['heatmap']
            char_names = [c['Name'] for c in results['characters']]
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Scene (Sampled)", y="Identity", color="Presence"),
                y=char_names,
                color_continuous_scale="Viridis",
                aspect="auto"
            )
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', family='Inter'))
            st.plotly_chart(fig, use_container_width=True)

        with chart_col2:
            st.markdown("""
            <div class="fade-in">
                <h3>⏱️ Identity Timeline</h3>
            </div>
            """, unsafe_allow_html=True)

            timeline_df = results['timeline']
            fig_timeline = px.timeline(
                timeline_df,
                x_start="Start",
                x_end="End",
                y="Character",
                color="Character",
                title=""
            )
            fig_timeline.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', family='Inter'), showlegend=False)
            st.plotly_chart(fig_timeline, use_container_width=True)


def format_literal_results(final_data, total_scenes, duration):
    """Transform literal pipeline data into dashboard format."""
    unique_ids = sorted(list(set([p['global_identity_id'] for p in final_data])))
    
    chars = []
    heatmap = np.zeros((len(unique_ids), 10)) # Sampled to 10 scene points for heatmap
    timeline_entries = []
    
    import datetime
    base_time = datetime.datetime(2024, 1, 1)

    for i, idx in enumerate(unique_ids):
        segments = [p for p in final_data if p['global_identity_id'] == idx]
        scr_time = sum([p['end'] - p['start'] for p in segments])
        
        chars.append({
            "ID": f"CHAR_{idx:03d}",
            "Name": f"Character {idx}",
            "Appearances": len(segments),
            "Screen Time": f"{scr_time:.1f}s",
            "Matched Speaker": segments[0].get('matched_speaker', 'None'),
            "thumbnail": segments[0]['thumbnail']
        })
        
        for seg in segments:
            # Fill heatmap
            scene_idx = seg['scene_id']
            if scene_idx < 10:
                heatmap[i, scene_idx] = 1
                
            # Fill timeline
            timeline_entries.append({
                "Character": f"Character {idx}",
                "Start": base_time + datetime.timedelta(seconds=seg['start']),
                "End": base_time + datetime.timedelta(seconds=seg['end']),
                "Confidence": 0.9 # Placeholder for cluster confidence
            })

    return {
        "characters": chars,
        "total_scenes": total_scenes,
        "num_segments": len(final_data),
        "heatmap": heatmap,
        "timeline": pd.DataFrame(timeline_entries) if timeline_entries else pd.DataFrame(columns=["Character", "Start", "End"])
    }
