import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# CORS configuration
CORS(app, 
     resources={
         r"/api/*": {
             "origins": "*",
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type"]
         }
     })

# Import blueprints
from app.backend.api.generate import generate_bp
from app.backend.api.video import video_bp

app.register_blueprint(generate_bp)
app.register_blueprint(video_bp)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Apparel Pipeline API"}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)