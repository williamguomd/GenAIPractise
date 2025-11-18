"""
Video Processor - Extracts frames from videos and encodes them for LLM
"""

import base64
from pathlib import Path
from typing import List, Optional
import cv2
from PIL import Image
import io


class VideoProcessor:
    """Processes videos for LLM analysis by extracting frames"""
    
    def __init__(self, max_frames: int = 10):
        """
        Initialize the video processor
        
        Args:
            max_frames: Maximum number of frames to extract from video
        """
        self.max_frames = max_frames
    
    def extract_frames(self, video_path: Path) -> List[Image.Image]:
        """
        Extract frames from a video file
        
        Args:
            video_path: Path to the video file
        
        Returns:
            List of PIL Image objects
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 1
        
        # Calculate frame interval to extract evenly spaced frames
        if total_frames > self.max_frames:
            interval = total_frames // self.max_frames
        else:
            interval = 1
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract frame at intervals
            if frame_count % interval == 0:
                # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        
        if not frames:
            raise ValueError(f"No frames extracted from video: {video_path}")
        
        return frames
    
    def encode_image_to_base64(self, image: Image.Image, format: str = "JPEG") -> str:
        """
        Encode a PIL Image to base64 string
        
        Args:
            image: PIL Image object
            format: Image format (JPEG, PNG, etc.)
        
        Returns:
            Base64 encoded string with data URI prefix
        """
        buffered = io.BytesIO()
        image.save(buffered, format=format)
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        # Return with data URI prefix for OpenAI API
        mime_type = f"image/{format.lower()}"
        return f"data:{mime_type};base64,{img_base64}"
    
    def process_video(self, video_path: Path) -> List[str]:
        """
        Process video and return base64 encoded frames
        
        Args:
            video_path: Path to the video file
        
        Returns:
            List of base64 encoded image strings (with data URI prefix)
        """
        frames = self.extract_frames(video_path)
        encoded_frames = [self.encode_image_to_base64(frame) for frame in frames]
        return encoded_frames

