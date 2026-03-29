import cv2
import os
from scenedetect import detect, ContentDetector, SceneManager, open_video
from tqdm import tqdm

def find_scenes(video_path, threshold=27.0):
    """Detect scenes in a video using PySceneDetect."""
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video=video)
    scene_list = scene_manager.get_scene_list()
    return scene_list

def extract_keyframes(video_path, scene_list, output_dir):
    """Extract keyframes (middle of the scene) for each detected scene."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    cap = cv2.VideoCapture(video_path)
    keyframes = []
    
    for i, scene in enumerate(scene_list):
        start_frame, end_frame = scene[0].get_frames(), scene[1].get_frames()
        # Pick the middle frame as the keyframe
        middle_frame = (start_frame + end_frame) // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
        ret, frame = cap.read()
        if ret:
            img_path = os.path.join(output_dir, f"scene_{i}.jpg")
            cv2.imwrite(img_path, frame)
            keyframes.append({"scene_id": i, "img_path": img_path, "timestamp": middle_frame / cap.get(cv2.CAP_PROP_FPS)})
            
    cap.release()
    return keyframes

def get_video_info(video_path):
    """Retrieve basic video metadata."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    return {"fps": fps, "frame_count": frame_count, "duration": duration}
