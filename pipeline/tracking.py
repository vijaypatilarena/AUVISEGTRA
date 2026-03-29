import cv2
import numpy as np
import os
from ultralytics import YOLO

class Tracker:
    def __init__(self, model_version='yolov8n.pt'):
        """Initialize the YOLOv8 model for person detection."""
        self.model = YOLO(model_version)
        self.classes = [0] # Class 0 is 'person'

    def track_persons(self, scene_video_path, output_dir=None):
        """Track persons in a specific scene video using YOLOv8 and ByteTrack."""
        # Use YOLO's built-in tracking support (ByteTrack)
        results = self.model.track(source=scene_video_path, persist=True, classes=self.classes, tracker="bytetrack.yaml")
        
        tracked_frames = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            if boxes.id is not None:
                frame_data = {
                    "frame_id": int(result.path.split('/')[-1].split('.')[0]) if '/' in result.path else 0,
                    "detections": []
                }
                for box, track_id in zip(boxes.xyxy, boxes.id):
                    frame_data["detections"].append({
                        "id": int(track_id),
                        "box": [float(b) for b in box] # [x1, y1, x2, y2]
                    })
                tracked_frames.append(frame_data)
        
        return tracked_frames

    def extract_person_crops(self, frame, detection_boxes, scene_id, frame_id, output_dir):
        """Extract and save person crops for ReID."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        crops = []
        for i, box in enumerate(detection_boxes):
            x1, y1, x2, y2 = map(int, box)
            crop = frame[y1:y2, x1:x2]
            if crop.size > 0:
                crop_path = os.path.join(output_dir, f"scene_{scene_id}_frame_{frame_id}_person_{i}.jpg")
                cv2.imwrite(crop_path, crop)
                crops.append(crop_path)
        return crops
