"""
Enhanced Backend Features for MoneyPrinter
Add these improvements to existing Backend modules

This file demonstrates practical enhancements you can implement
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, send_file
from functools import wraps

# Enhanced error handling and logging
class VideoGenerationError(Exception):
    """Custom exception for video generation errors"""
    def __init__(self, message: str, error_code: str = "GENERATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ProgressTracker:
    """Track and report video generation progress"""
    
    def __init__(self):
        self.progress_file = "../temp/progress.json"
        self.steps = [
            "Generating script...",
            "Searching for videos...", 
            "Downloading videos...",
            "Creating audio...",
            "Generating subtitles...",
            "Assembling final video...",
            "Complete!"
        ]
        
    def update_progress(self, step: int, message: str = None):
        """Update progress and save to file"""
        progress_data = {
            "step": step,
            "total_steps": len(self.steps),
            "percentage": int((step / len(self.steps)) * 100),
            "message": message or self.steps[min(step, len(self.steps) - 1)],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f)
        except Exception as e:
            logging.warning(f"Could not save progress: {e}")
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "step": 0,
            "total_steps": len(self.steps),
            "percentage": 0,
            "message": "Starting...",
            "timestamp": datetime.now().isoformat()
        }

# Enhanced video generation with better error handling
def generate_video_enhanced(video_subject: str, voice: str, automate_youtube: bool = False) -> Dict:
    """Enhanced video generation with progress tracking and error handling"""
    
    progress = ProgressTracker()
    
    try:
        # Step 1: Generate script
        progress.update_progress(1, "Generating engaging script...")
        script = generate_script_with_retry(video_subject)
        if not script:
            raise VideoGenerationError("Failed to generate script")
        
        # Step 2: Search for videos
        progress.update_progress(2, "Finding relevant stock videos...")
        search_terms = get_search_terms(video_subject, 5, script)
        video_urls = search_videos_enhanced(search_terms)
        
        if len(video_urls) < 3:
            raise VideoGenerationError("Not enough videos found. Try a different topic.")
        
        # Step 3: Download videos
        progress.update_progress(3, f"Downloading {len(video_urls)} videos...")
        video_paths = download_videos_with_progress(video_urls, progress)
        
        # Step 4: Create audio
        progress.update_progress(4, "Creating text-to-speech audio...")
        audio_path = create_audio_enhanced(script, voice)
        
        # Step 5: Generate subtitles
        progress.update_progress(5, "Generating synchronized subtitles...")
        subtitles_path = generate_subtitles_enhanced(audio_path, script)
        
        # Step 6: Assemble video
        progress.update_progress(6, "Assembling final video...")
        final_video_path = assemble_video_enhanced(video_paths, audio_path, subtitles_path)
        
        # Step 7: Upload if requested
        if automate_youtube:
            progress.update_progress(7, "Uploading to YouTube...")
            upload_result = upload_to_youtube_enhanced(final_video_path, video_subject, script)
        
        progress.update_progress(len(progress.steps) - 1, "Video generation complete!")
        
        return {
            "status": "success",
            "video_path": final_video_path,
            "message": "Video generated successfully!",
            "metadata": {
                "duration": get_video_duration(final_video_path),
                "resolution": get_video_resolution(final_video_path),
                "file_size": get_file_size(final_video_path)
            }
        }
        
    except VideoGenerationError as e:
        logging.error(f"Video generation failed: {e.message}")
        return {
            "status": "error",
            "error_code": e.error_code,
            "message": e.message,
            "suggestions": get_error_suggestions(e.error_code)
        }
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "error_code": "UNKNOWN_ERROR",
            "message": "An unexpected error occurred",
            "suggestions": ["Try again in a few minutes", "Check your internet connection"]
        }

def generate_script_with_retry(video_subject: str, max_retries: int = 3) -> Optional[str]:
    """Generate script with retry logic"""
    for attempt in range(max_retries):
        try:
            script = generate_script(video_subject)
            if script and len(script.strip()) > 50:  # Minimum length check
                return script
        except Exception as e:
            logging.warning(f"Script generation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
    
    return None

def search_videos_enhanced(search_terms: List[str]) -> List[str]:
    """Enhanced video search with fallback terms"""
    video_urls = []
    
    # Primary search
    for term in search_terms:
        urls = search_for_stock_videos(term, os.getenv("PEXELS_API_KEY"), 15, 10)
        video_urls.extend(urls[:2])  # Limit per term
    
    # If not enough videos, try broader search terms
    if len(video_urls) < 3:
        fallback_terms = ["nature", "city", "technology", "abstract", "motion"]
        for term in fallback_terms:
            if len(video_urls) >= 5:
                break
            urls = search_for_stock_videos(term, os.getenv("PEXELS_API_KEY"), 10, 5)
            video_urls.extend(urls[:1])
    
    return list(set(video_urls))  # Remove duplicates

def download_videos_with_progress(video_urls: List[str], progress: ProgressTracker) -> List[str]:
    """Download videos with progress updates"""
    video_paths = []
    total_videos = len(video_urls)
    
    for i, url in enumerate(video_urls):
        try:
            progress.update_progress(3, f"Downloading video {i+1}/{total_videos}...")
            path = save_video(url)
            video_paths.append(path)
        except Exception as e:
            logging.warning(f"Failed to download video {i+1}: {e}")
    
    return video_paths

# Add these utility functions
def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        from moviepy.editor import VideoFileClip
        with VideoFileClip(video_path) as clip:
            return clip.duration
    except:
        return 0.0

def get_video_resolution(video_path: str) -> str:
    """Get video resolution"""
    try:
        from moviepy.editor import VideoFileClip
        with VideoFileClip(video_path) as clip:
            return f"{clip.w}x{clip.h}"
    except:
        return "unknown"

def get_file_size(file_path: str) -> str:
    """Get file size in human readable format"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "unknown"

def get_error_suggestions(error_code: str) -> List[str]:
    """Get helpful suggestions based on error code"""
    suggestions = {
        "GENERATION_ERROR": [
            "Try a different topic or make it more specific",
            "Check your internet connection",
            "Ensure all API keys are configured correctly"
        ],
        "SCRIPT_ERROR": [
            "Try a simpler topic description",
            "Check if GPT service is available",
            "Make sure your topic is in English"
        ],
        "VIDEO_SEARCH_ERROR": [
            "Try a different topic with more common keywords",
            "Check your Pexels API key",
            "Try again in a few minutes"
        ],
        "AUDIO_ERROR": [
            "Check your TikTok session ID",
            "Try a different voice option",
            "Ensure text is not too long"
        ]
    }
    
    return suggestions.get(error_code, ["Try again later", "Contact support if the issue persists"])

# Enhanced API endpoints
@app.route("/api/progress", methods=["GET"])
def get_progress():
    """Get current generation progress"""
    progress = ProgressTracker()
    return jsonify(progress.get_progress())

@app.route("/api/health", methods=["GET"]) 
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "pexels_api": bool(os.getenv("PEXELS_API_KEY")),
            "tiktok_session": bool(os.getenv("TIKTOK_SESSION_ID")),
            "imagemagick": bool(os.getenv("IMAGEMAGICK_BINARY")),
            "assembly_ai": bool(os.getenv("ASSEMBLY_AI_API_KEY"))
        }
    })

@app.route("/api/video/<video_id>", methods=["GET"])
def get_video(video_id: str):
    """Serve generated video file"""
    try:
        video_path = f"../temp/{video_id}"
        if os.path.exists(video_path):
            return send_file(video_path, as_attachment=True)
        else:
            return jsonify({"error": "Video not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rate limiting decorator
from functools import wraps
from collections import defaultdict
import time

# Simple in-memory rate limiter
request_counts = defaultdict(list)

def rate_limit(max_requests: int = 5, window_minutes: int = 10):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Clean old requests
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip] 
                if req_time > window_start
            ]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {max_requests} requests per {window_minutes} minutes"
                }), 429
            
            # Add current request
            request_counts[client_ip].append(now)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Usage example:
# @app.route("/api/generate", methods=["POST"])
# @rate_limit(max_requests=3, window_minutes=15)
# def generate():
#     # Your generation logic here

"""
Implementation Instructions:

1. Add these functions to your existing Backend/main.py
2. Replace the current generate() function with generate_video_enhanced()
3. Add the new API endpoints for progress tracking and health checks
4. Implement proper logging configuration
5. Add rate limiting to prevent abuse

Example integration:

# In main.py, replace the generate endpoint:
@app.route("/api/generate", methods=["POST"])
@rate_limit(max_requests=3, window_minutes=15)
def generate():
    data = request.get_json()
    result = generate_video_enhanced(
        video_subject=data["videoSubject"],
        voice=data.get("voice", "en_us_001"),
        automate_youtube=data.get("automateYoutubeUpload", False)
    )
    return jsonify(result)
"""