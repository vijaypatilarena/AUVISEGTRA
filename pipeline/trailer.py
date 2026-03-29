import os
import subprocess
import json
import requests
import cv2
import numpy as np
from groq import Groq
from moviepy import VideoFileClip

class TrailerIntelligence:
    def __init__(self, groq_api_key=None):
        """Initialize the Trailer Intelligence component."""
        self.client = None
        if groq_api_key:
            self.client = Groq(api_key=groq_api_key)

    def download_trailer(self, url, output_dir):
        """Download YouTube trailer using yt-dlp with unique filenames."""
        import hashlib
        video_id = hashlib.md5(url.encode()).hexdigest()[:10]
        output_file = os.path.join(output_dir, f"trailer_{video_id}.mp4")
        
        # Download video and metadata
        command = f"yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' --write-info-json --output {output_file} {url}"
        subprocess.run(command, shell=True, check=True)
        
        metadata = {}
        info_json = f"{output_file}.info.json"
        if os.path.exists(info_json):
            with open(info_json, 'r') as f:
                metadata = json.load(f)
            os.remove(info_json)
            
        return output_file, metadata

    def get_transcript(self, audio_path):
        """Use Whisper (via Groq) to transcribe speaker dialogue."""
        if not self.client:
            return "Transcription failed. Missing API key."
            
        with open(audio_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3",
                response_format="json",
                language="en",
                temperature=0.0
            )
        return transcription.text

    def analyze_trailer(self, transcript, scene_descriptions, metadata=None, language="English"):
        """Prompt LLM (Groq) for genre classification, summary, and storyline prediction."""
        title = metadata.get('title', 'Unknown Title') if metadata else 'Unknown Title'
        description = metadata.get('description', '') if metadata else ''
        
        if not self.client:
            return {
                "genre": "System in Demo Mode",
                "confidence": 0.5,
                "summary": f"Could not analyze '{title}' because Groq API key is missing. Please enter your key in the sidebar for full intelligence.",
                "storyline": "Full storyline analysis requires a valid Groq API key to process the transcript and visual context."
            }
            
        prompt = f"""
        Analyze the following movie trailer data for the film: "{title}"
        
        Metadata Description: {description[:500]}
        
        Transcript (Whisper):
        {transcript}
        
        Visual Insights:
        {scene_descriptions}
        
        Please provide the response in {language}.
        Return ONLY a JSON object with the following fields:
        "genre": Predicted genres (comma-separated),
        "confidence": Confidence score (0-1),
        "summary": Concise summary (1-2 sentences),
        "storyline": Detailed predicted narrative arc and storyline progression based on the trailer clues.
        """
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert film analyst providing multimodal intelligence on cinema trailers."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        return json.loads(chat_completion.choices[0].message.content)

    def extract_visual_features(self, video_path):
        """Analyze visuals with PySceneDetect, YOLOv8 (person count), and intensity."""
        from scenedetect import detect, ContentDetector
        from ultralytics import YOLO
        
        # 1. Detect Scenes
        scene_list = detect(video_path, ContentDetector())
        num_scenes = len(scene_list)
        
        # 2. Person Detection (YOLOv8) & Intensity
        model = YOLO("yolov8n.pt") # Small model for speed
        cap = cv2.VideoCapture(video_path)
        intensity = []
        max_people = 0
        count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Sample every 30th frame (roughly once per second)
            if count % 30 == 0:
                # Intensity (Brightness)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                intensity.append(np.mean(gray))
                
                # Person Count
                results = model(frame, classes=[0], verbose=False) # class 0 is person
                person_count = len(results[0].boxes) if results else 0
                max_people = max(max_people, person_count)
                
            count += 1
        cap.release()
        
        return {
            "mean_intensity": float(np.mean(intensity)) if intensity else 0,
            "peak_intensity": float(np.max(intensity)) if intensity else 0,
            "num_scenes": num_scenes,
            "max_characters": max_people,
            "complexity": "High" if num_scenes > 15 else "Moderate" if num_scenes > 5 else "Low"
        }
