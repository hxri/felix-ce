from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime
import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app.backend.api.outfits import get_outfit_image

video_bp = Blueprint('video', __name__)

VIDEO_JOB_STORE = {}

@video_bp.route('/api/video', methods=['POST'])
def generate_video():
    """
    POST /api/video
    Body: {
        "image_file": "<FAL image URL>",
        "outfit_top": "Blue T-Shirt",
        "outfit_bottom": "Black Jeans",
        "motion_description": "person turns around smiling"
    }
    """
    try:
        data = request.json
        job_id = str(uuid.uuid4())
        
        if not data.get('image_file'):
            return jsonify({"error": "image_file required"}), 400
        
        from src.services.pipelines.video_pipeline import VideoPipeline
        
        # Build apparel description from outfit names
        outfit_top = data.get('outfit_top', 'casual top')
        outfit_bottom = data.get('outfit_bottom', 'casual bottom')
        apparel_desc = f"{outfit_top} with {outfit_bottom}"
        
        print(f"[VIDEO] Image URL: {data.get('image_file')}")
        print(f"[VIDEO] Apparel: {apparel_desc}")
        print(f"[VIDEO] Motion: {data.get('motion_description', '')}")
        
        VIDEO_JOB_STORE[job_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            pipeline = VideoPipeline(video_model=data.get('model', 'grok'))
            result = pipeline.run(
                reference_image=data['image_file'],  # Using FAL image URL
                apparel_description=apparel_desc,
                motion_description=data.get('motion_description', ''),
                duration_sec=int(data.get('duration_sec', 4)),
                no_download=data.get('no_download', False),
            )
            
            print(f"[VIDEO] Full result keys: {result.keys()}")
            
            # Extract video URL directly from FAL response
            video_url = None
            
            if result.get('raw_response', {}).get('video', {}).get('url'):
                video_url = result['raw_response']['video']['url']
                print(f"[VIDEO] Extracted FAL URL: {video_url}")
            
            if not video_url:
                print(f"[VIDEO] ERROR: Could not extract video URL")
                print(f"[VIDEO] Result structure: {json.dumps(result, indent=2, default=str)}")
                raise ValueError("Could not extract video URL from FAL response")
            
            VIDEO_JOB_STORE[job_id].update({
                "status": "completed",
                "video_file": video_url,
                "latency_sec": result.get('latency_sec', 0)
            })
            
            print(f"[VIDEO] Success: {video_url}")
            
        except Exception as e:
            VIDEO_JOB_STORE[job_id].update({
                "status": "failed",
                "error": str(e)
            })
            print(f"[VIDEO] Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        return jsonify({
            "job_id": job_id,
            "status": "processing"
        }), 202
    
    except Exception as e:
        print(f"[VIDEO] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@video_bp.route('/api/video/status/<job_id>', methods=['GET'])
def get_video_status(job_id):
    """GET /api/video/status/<job_id>"""
    if job_id not in VIDEO_JOB_STORE:
        return jsonify({"error": "Job not found"}), 404
    
    job = VIDEO_JOB_STORE[job_id]
    return jsonify({
        "job_id": job_id,
        "status": job['status'],
        "video_file": job.get('video_file'),
        "latency_sec": job.get('latency_sec'),
        "error": job.get('error')
    }), 200