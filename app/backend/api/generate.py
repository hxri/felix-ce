from flask import Blueprint, request, jsonify
import json
import os
import sys
import uuid
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app.backend.api.outfits import get_outfit_image

generate_bp = Blueprint('generate', __name__)

JOB_STORE = {}

@generate_bp.route('/api/generate', methods=['POST'])
def generate_image():
    """
    POST /api/generate
    Body: {
        "person_image": "<base64>",
        "outfit_top": "Blue T-Shirt",
        "outfit_bottom": "Black Jeans",
        "background": "Urban Cafe",
        "environment": "professional lighting, studio"
    }
    """
    try:
        data = request.json
        job_id = str(uuid.uuid4())
        
        if not data.get('person_image'):
            return jsonify({"error": "person_image required"}), 400
        
        # Import pipeline
        from src.services.pipelines.image_pipeline import ImagePipeline
        from src.schemas.person import PersonAttributes
        from src.schemas.environment import EnvironmentAttributes
        
        # Get actual outfit images from database
        outfit_top_name = data.get('outfit_top', 'casual')
        outfit_bottom_name = data.get('outfit_bottom', 'casual')
        
        outfit_top_image = get_outfit_image(outfit_top_name)
        outfit_bottom_image = get_outfit_image(outfit_bottom_name)
        
        print(f"[GENERATE] Top: {outfit_top_name} -> {outfit_top_image}")
        print(f"[GENERATE] Bottom: {outfit_bottom_name} -> {outfit_bottom_image}")
        
        JOB_STORE[job_id] = {
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            pipeline = ImagePipeline()
            result = pipeline.run(
                person=PersonAttributes(height_cm=175, weight_kg=85, gender="male", age=26),
                env=EnvironmentAttributes(
                    apparel_type=f"{outfit_top_name} with {outfit_bottom_name}",
                    inferred_setting=data.get('background', 'studio'),
                    visual_cues=data.get('environment', 'professional lighting')
                ),
                description="Full body portrait",
                person_reference_image=data['person_image'],
                outfit_reference_images=[outfit_top_image, outfit_bottom_image],
                no_download=data.get('no_download', False),
            )
            
            print(f"[GENERATE] Full result keys: {result.keys()}")
            
            # Extract image URL directly from FAL response
            image_url = None
            
            if result.get('raw_response', {}).get('images', []):
                image_url = result['raw_response']['images'][0].get('url')
                print(f"[GENERATE] Extracted FAL URL: {image_url}")
            
            if not image_url:
                print(f"[GENERATE] ERROR: Could not extract image URL")
                print(f"[GENERATE] Result structure: {json.dumps(result, indent=2, default=str)}")
                raise ValueError("Could not extract image URL from FAL response")
            
            JOB_STORE[job_id].update({
                "status": "completed",
                "image_file": image_url,
                "latency_sec": result.get('latency_sec', 0)
            })
            
            print(f"[GENERATE] Success: {image_url}")
            
        except Exception as e:
            JOB_STORE[job_id].update({
                "status": "failed",
                "error": str(e)
            })
            print(f"[GENERATE] Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        return jsonify({
            "job_id": job_id,
            "status": "processing",
            "message": "Image generation started"
        }), 202
    
    except Exception as e:
        print(f"[GENERATE] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@generate_bp.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """GET /api/status/<job_id>"""
    if job_id not in JOB_STORE:
        return jsonify({"error": "Job not found"}), 404
    
    job = JOB_STORE[job_id]
    return jsonify({
        "job_id": job_id,
        "status": job['status'],
        "image_file": job.get('image_file'),
        "latency_sec": job.get('latency_sec'),
        "error": job.get('error')
    }), 200