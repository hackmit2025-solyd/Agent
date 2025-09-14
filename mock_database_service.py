"""
Mock Database Service for Healthcare Agent System
Simulates Ryan's Database Service for testing.
"""
from flask import Flask, request, jsonify
import json
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Mock patient database
MOCK_PATIENTS = {
    "PAT001": {
        "patient_id": "PAT001",
        "name": "John Smith",
        "last_visit": "2024-01-10",
        "status": "active",
        "medical_history": ["Diabetes Type 2", "Hypertension"],
        "current_medications": ["Metformin", "Lisinopril"],
        "symptoms": ["blurred vision", "fatigue"],
        "age": 45,
        "follow_up_reason": "diabetes_management"
    },
    "PAT002": {
        "patient_id": "PAT002",
        "name": "Sarah Johnson",
        "last_visit": "2024-01-08",
        "status": "active",
        "medical_history": ["Diabetes Type 1", "Diabetic Retinopathy"],
        "current_medications": ["Insulin", "Metformin"],
        "symptoms": ["vision problems", "numbness"],
        "age": 38,
        "follow_up_reason": "vision_complications"
    },
    "PAT003": {
        "patient_id": "PAT003",
        "name": "Michael Chen",
        "last_visit": "2024-01-05",
        "status": "active",
        "medical_history": ["Heart Disease", "High Cholesterol"],
        "current_medications": ["Atorvastatin", "Aspirin"],
        "symptoms": ["chest pain", "shortness of breath"],
        "age": 52,
        "follow_up_reason": "cardiac_monitoring"
    },
    "PAT004": {
        "patient_id": "PAT004",
        "name": "Elena Rodriguez",
        "last_visit": "2024-01-12",
        "status": "active",
        "medical_history": ["Depression", "Anxiety"],
        "current_medications": ["Sertraline", "Lorazepam"],
        "symptoms": ["mood changes", "sleep problems"],
        "age": 29,
        "follow_up_reason": "mental_health_check"
    }
}

@app.route('/api/query', methods=['POST'])
def query_patients():
    """Query patients based on doctor's request."""
    try:
        data = request.get_json()
        query = data.get('query', '').lower()
        
        print(f"📊 Database received query: {query}")
        
        # Parse query and filter patients
        matching_patients = []
        
        # Check for diabetes-related queries
        if 'diabetic' in query or 'diabetes' in query:
            for patient in MOCK_PATIENTS.values():
                if any('diabetes' in condition.lower() for condition in patient['medical_history']):
                    matching_patients.append(patient)
        
        # Check for vision-related queries
        elif 'vision' in query or 'eye' in query:
            for patient in MOCK_PATIENTS.values():
                if any('vision' in symptom.lower() or 'eye' in symptom.lower() for symptom in patient['symptoms']):
                    matching_patients.append(patient)
        
        # Check for heart-related queries
        elif 'heart' in query or 'cardiac' in query:
            for patient in MOCK_PATIENTS.values():
                if any('heart' in condition.lower() for condition in patient['medical_history']):
                    matching_patients.append(patient)
        
        # Check for mental health queries
        elif 'depression' in query or 'anxiety' in query or 'mental' in query:
            for patient in MOCK_PATIENTS.values():
                if any(condition.lower() in ['depression', 'anxiety'] for condition in patient['medical_history']):
                    matching_patients.append(patient)
        
        # If no specific condition mentioned, return all patients
        else:
            matching_patients = list(MOCK_PATIENTS.values())
        
        # Filter by time if mentioned
        if 'last week' in query or 'recent' in query:
            # Filter to patients seen in last 7 days
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            matching_patients = [p for p in matching_patients if p['last_visit'] >= cutoff_date]
        
        print(f"✅ Found {len(matching_patients)} matching patients")
        
        return jsonify({
            "success": True,
            "query": query,
            "patients": matching_patients,
            "count": len(matching_patients),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Database query error: {str(e)}")
        return jsonify({
            "error": "database_query_failed",
            "message": str(e),
            "patients": [],
            "count": 0
        }), 500

@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    """Get all patients."""
    return jsonify({
        "success": True,
        "patients": list(MOCK_PATIENTS.values()),
        "count": len(MOCK_PATIENTS)
    })

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get specific patient by ID."""
    if patient_id in MOCK_PATIENTS:
        return jsonify({
            "success": True,
            "patient": MOCK_PATIENTS[patient_id]
        })
    else:
        return jsonify({
            "error": "patient_not_found",
            "message": f"Patient {patient_id} not found"
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "mock_database_service",
        "timestamp": datetime.now().isoformat(),
        "patients_available": len(MOCK_PATIENTS)
    })

if __name__ == '__main__':
    print("🗄️ Starting Mock Database Service...")
    print("📡 Available at: http://localhost:3000")
    print("🔧 Endpoints:")
    print("   POST /api/query - Query patients")
    print("   GET /api/patients - Get all patients")
    print("   GET /api/patients/<id> - Get specific patient")
    print("   GET /health - Health check")
    print("\n🎉 Mock Database Service ready!")
    
    app.run(debug=True, host='127.0.0.1', port=3000)
