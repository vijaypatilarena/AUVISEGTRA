import os
import subprocess
import librosa
import numpy as np
from pyannote.audio import Pipeline
from moviepy import VideoFileClip

class AudioProcessor:
    def __init__(self, hf_token=None):
        """Initialize the audio pipeline (Speaker Diarization)."""
        self.hf_token = hf_token # Required for pretrained models
        self.diarization_pipeline = None
        
        if self.hf_token:
            # Requires accepted terms on HF model page
            try:
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization@2.1",
                    use_auth_token=self.hf_token
                )
            except Exception as e:
                print(f"Error loading pyannote pipeline: {e}")

    def extract_audio(self, video_path, output_audio_path):
        """Extract MP3 audio from a video using MoviePy (compressed to stay under API limits)."""
        video = VideoFileClip(video_path)
        # Use mp3 with lower bitrate to keep file size small for Groq/Whisper
        video.audio.write_audiofile(output_audio_path, codec='libmp3lame', bitrate='64k')
        
        return output_audio_path

    def diarize_audio(self, audio_path):
        """Perform speaker diarization to find out who spoke when."""
        if not self.diarization_pipeline:
            # Fallback for mock diarization results
            return [{"speaker": "SPEAKER_00", "start": 0.0, "end": 5.0, "embedding": np.random.rand(128)}]
            
        diarization = self.diarization_pipeline(audio_path)
        
        results = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Also extract speaker embeddings (MFCC-based or more advanced)
            # Embedding should be extracted locally from the segment
            start, end = turn.start, turn.end
            y, sr = librosa.load(audio_path, sr=None, offset=start, duration=end-start)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=128)
            embedding = np.mean(mfcc, axis=1)
            
            results.append({
                "speaker": speaker,
                "start": start,
                "end": end,
                "embedding": embedding
            })
            
        return results

    def extract_mfcc_intensity(self, audio_path):
        """Extract MFCC and overall intensity for the trailer analysis."""
        y, sr = librosa.load(audio_path)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        rms = librosa.feature.rms(y=y)
        intensity = np.mean(rms)
        
        return {
            "mfccs": np.mean(mfccs, axis=1).tolist(),
            "intensity": float(intensity)
        }
