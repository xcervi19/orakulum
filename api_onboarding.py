#!/usr/bin/env python3
"""
Orakulum Onboarding API Handler

Flask API endpoint that receives onboarding form submissions
and creates new leads in Supabase database.

Usage:
    python3 api_onboarding.py

Environment Variables:
    SUPABASE_URL - Supabase project URL
    SUPABASE_SERVICE_KEY - Supabase service key
    API_PORT - Port to run API server (default: 5000)
    CORS_ORIGINS - Allowed CORS origins (default: *)
"""

import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import dotenv

from pipeline.db import get_client, STATUS_FLAGGED

dotenv.load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Configuration
API_PORT = int(os.getenv("API_PORT", 5000))


@app.route('/api/leads', methods=['POST'])
def create_lead():
    """
    Create a new lead from onboarding form submission.
    
    Expected JSON payload:
    {
        "name": "Jan Novák",
        "email": "jan@example.com",
        "description": "Full description with goals...",
        "input_transform": {
            "obor": "Frontend Development",
            "seniorita": "Začátečník",
            "hlavni_cil": "První práce v IT",
            "casovy_horizont": "6 měsíců",
            "technologie": [],
            "raw_description": "Original user description"
        },
        "status": "FLAGGED"
    }
    
    Returns:
        201: Lead created successfully
        400: Invalid request data
        500: Server error
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'description']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate email format
        email = data['email'].strip()
        if '@' not in email or '.' not in email:
            return jsonify({
                "error": "Invalid email format"
            }), 400
        
        # Generate unique ID
        lead_id = str(uuid.uuid4())
        
        # Prepare lead data
        lead_data = {
            "id": lead_id,
            "name": data['name'].strip(),
            "email": email,
            "description": data['description'].strip(),
            "status": data.get('status', STATUS_FLAGGED),
            "input_transform": data.get('input_transform', {}),
            "plan": None,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert into Supabase
        supabase = get_client()
        result = supabase.table("junior_leads").insert(lead_data).execute()
        
        if not result.data:
            raise Exception("Failed to insert lead into database")
        
        # Return success response
        return jsonify({
            "success": True,
            "lead_id": lead_id,
            "message": "Lead created successfully",
            "data": result.data[0]
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error creating lead: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "orakulum-onboarding-api"
    }), 200


@app.route('/api/leads/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    """
    Get lead details by ID.
    Useful for debugging or checking submission status.
    """
    try:
        supabase = get_client()
        result = supabase.table("junior_leads").select("*").eq("id", lead_id).single().execute()
        
        if not result.data:
            return jsonify({
                "error": "Lead not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": result.data
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching lead: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🔮 ORAKULUM ONBOARDING API")
    print("=" * 60)
    print(f"   Port: {API_PORT}")
    print(f"   CORS: {cors_origins}")
    print("=" * 60)
    print()
    print("Endpoints:")
    print(f"   POST   /api/leads       - Create new lead")
    print(f"   GET    /api/leads/<id>  - Get lead by ID")
    print(f"   GET    /api/health      - Health check")
    print()
    print("=" * 60)
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=API_PORT,
        debug=os.getenv("FLASK_ENV") == "development"
    )
