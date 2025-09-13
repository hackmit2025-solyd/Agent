"""
Healthcare Agent Flask Server
RESTful API for the LLM-powered healthcare agent system.
"""
from flask import Flask, request, jsonify
import asyncio
import json
from datetime import datetime
from agents.master_agent import MasterAgent, PatientRecord, ParsedCriteria
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from services.llm_service import llm_service

app = Flask(__name__)

# Global instances
master_agent = MasterAgent()
sub_agent_manager = SubAgentManager()

# Sample patients database (in production, this would be a real database)
patients_db = {
    "PAT001": PatientRecord(
        patient_id="PAT001",
        name="Sarah Johnson",
        last_visit="2024-01-15",
        status="active",
        medical_history=["Diabetes Type 2", "Hypertension"],
        current_medications=["Metformin", "Lisinopril"],
        symptoms=["blurred vision", "fatigue"]
    ),
    "PAT002": PatientRecord(
        patient_id="PAT002",
        name="Michael Chen",
        last_visit="2024-01-10",
        status="active",
        medical_history=["Heart Disease", "High Cholesterol"],
        current_medications=["Atorvastatin", "Aspirin"],
        symptoms=["chest pain", "shortness of breath"]
    ),
    "PAT003": PatientRecord(
        patient_id="PAT003",
        name="Elena Rodriguez",
        last_visit="2024-01-05",
        status="active",
        medical_history=["Depression", "Anxiety"],
        current_medications=["Sertraline", "Lorazepam"],
        symptoms=["mood changes", "sleep problems"]
    )
}

def run_async(coro):
    """Helper to run async functions in Flask."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/')
def home():
    """Home endpoint with API documentation."""
    return jsonify({
        "message": "Healthcare Agent API Server",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/parse-query": "Parse doctor's natural language query",
            "POST /api/create-sub-agent": "Create a sub-agent for a patient",
            "POST /api/process-communication": "Process communication with Claude",
            "GET /api/patients": "Get all patients",
            "GET /api/patients/<patient_id>": "Get specific patient",
            "GET /api/sub-agents": "Get all sub-agents",
            "GET /api/sub-agents/<agent_id>": "Get specific sub-agent",
            "POST /api/simulate-communication": "Simulate communication with JSON input",
            "GET /api/system-status": "Get system status"
        }
    })

@app.route('/api/parse-query', methods=['POST'])
def parse_query():
    """Parse a doctor's natural language query."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Query is required"}), 400
        
        query = data['query']
        
        # Parse with Claude
        parsed = run_async(master_agent.parse_doctor_query(query))
        
        return jsonify({
            "success": True,
            "query": query,
            "parsed_criteria": {
                "action": parsed.action,
                "time_filter": parsed.time_filter,
                "condition_filter": parsed.condition_filter,
                "symptom_filter": parsed.symptom_filter,
                "age_filter": parsed.age_filter,
                "medication_filter": parsed.medication_filter,
                "patient_criteria": parsed.patient_criteria
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """Get all patients."""
    try:
        patients = []
        for patient in patients_db.values():
            patients.append({
                "patient_id": patient.patient_id,
                "name": patient.name,
                "last_visit": patient.last_visit,
                "status": patient.status,
                "medical_history": patient.medical_history,
                "current_medications": patient.current_medications,
                "symptoms": patient.symptoms
            })
        
        return jsonify({
            "success": True,
            "patients": patients,
            "count": len(patients)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient."""
    try:
        if patient_id not in patients_db:
            return jsonify({"error": "Patient not found"}), 404
        
        patient = patients_db[patient_id]
        return jsonify({
            "success": True,
            "patient": {
                "patient_id": patient.patient_id,
                "name": patient.name,
                "last_visit": patient.last_visit,
                "status": patient.status,
                "medical_history": patient.medical_history,
                "current_medications": patient.current_medications,
                "symptoms": patient.symptoms
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/create-sub-agent', methods=['POST'])
def create_sub_agent():
    """Create a sub-agent for a patient."""
    try:
        data = request.get_json()
        if not data or 'patient_id' not in data:
            return jsonify({"error": "patient_id is required"}), 400
        
        patient_id = data['patient_id']
        if patient_id not in patients_db:
            return jsonify({"error": "Patient not found"}), 404
        
        # Create context from request or use default
        context_data = data.get('context', {
            "action": "follow_up",
            "time_filter": "today",
            "patient_criteria": {"status": "active"}
        })
        
        context = ParsedCriteria(
            action=context_data.get('action', 'follow_up'),
            time_filter=context_data.get('time_filter'),
            condition_filter=context_data.get('condition_filter'),
            symptom_filter=context_data.get('symptom_filter'),
            age_filter=context_data.get('age_filter'),
            medication_filter=context_data.get('medication_filter'),
            patient_criteria=context_data.get('patient_criteria', {"status": "active"})
        )
        
        # Create sub-agent
        patient = patients_db[patient_id]
        sub_agent = run_async(sub_agent_manager.create_sub_agent(patient, context))
        
        return jsonify({
            "success": True,
            "sub_agent": {
                "agent_id": sub_agent.sub_agent_id,
                "patient_id": sub_agent.patient_data.patient_id,
                "patient_name": sub_agent.patient_data.name,
                "status": sub_agent.status.value,
                "created_at": sub_agent.created_at.isoformat(),
                "context": {
                    "action": sub_agent.master_context.action,
                    "time_filter": sub_agent.master_context.time_filter,
                    "condition_filter": sub_agent.master_context.condition_filter,
                    "symptom_filter": sub_agent.master_context.symptom_filter
                }
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-communication', methods=['POST'])
def process_communication():
    """Process communication with Claude."""
    try:
        data = request.get_json()
        if not data or 'agent_id' not in data:
            return jsonify({"error": "agent_id is required"}), 400
        
        agent_id = data['agent_id']
        
        # Find sub-agent
        sub_agent = None
        for agent in sub_agent_manager.sub_agents.values():
            if agent.sub_agent_id == agent_id:
                sub_agent = agent
                break
        
        if not sub_agent:
            return jsonify({"error": "Sub-agent not found"}), 404
        
        # Process communication
        result = run_async(sub_agent.initiate_communication())
        
        return jsonify({
            "success": True,
            "communication_result": {
                "session_id": result.session_id,
                "patient_id": result.patient_id,
                "status": result.status.value,
                "outcome": result.outcome.value,
                "confidence_score": result.confidence_score,
                "data_obtained": result.data_obtained,
                "missing_data": result.missing_data,
                "timestamp": result.timestamp.isoformat(),
                "notes": result.notes
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate-communication', methods=['POST'])
def simulate_communication():
    """Simulate communication with JSON input from external server."""
    try:
        data = request.get_json()
        if not data or 'agent_id' not in data or 'communication_data' not in data:
            return jsonify({"error": "agent_id and communication_data are required"}), 400
        
        agent_id = data['agent_id']
        communication_data = data['communication_data']
        
        # Find sub-agent
        sub_agent = None
        for agent in sub_agent_manager.sub_agents.values():
            if agent.sub_agent_id == agent_id:
                sub_agent = agent
                break
        
        if not sub_agent:
            return jsonify({"error": "Sub-agent not found"}), 404
        
        # Simulate the communication processing
        patient_data = {
            "name": sub_agent.patient_data.name,
            "medical_history": sub_agent.patient_data.medical_history,
            "current_medications": sub_agent.patient_data.current_medications,
            "symptoms": sub_agent.patient_data.symptoms or []
        }
        
        # Let Claude analyze the communication
        claude_analysis = run_async(llm_service.analyze_communication_outcome(communication_data, patient_data))
        
        # Determine outcome
        outcome_str = claude_analysis.get("outcome", "close_loop").lower()
        decision_outcome = DecisionOutcome(outcome_str) if outcome_str in [o.value for o in DecisionOutcome] else DecisionOutcome.CLOSE_LOOP
        
        # Determine status
        if decision_outcome == DecisionOutcome.CLOSE_LOOP:
            status = FollowUpStatus.COMPLETED
        elif decision_outcome == DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW:
            status = FollowUpStatus.FLAGGED_FOR_REVIEW
        elif decision_outcome == DecisionOutcome.ESCALATE_URGENT:
            status = FollowUpStatus.FLAGGED_FOR_REVIEW
        else:
            status = FollowUpStatus.FAILED
        
        return jsonify({
            "success": True,
            "simulation_result": {
                "agent_id": agent_id,
                "patient_id": sub_agent.patient_data.patient_id,
                "patient_name": sub_agent.patient_data.name,
                "status": status.value,
                "outcome": decision_outcome.value,
                "confidence": claude_analysis.get("confidence", 0.0),
                "reasoning": claude_analysis.get("reasoning", "No reasoning provided"),
                "urgent_conditions": claude_analysis.get("urgent_conditions", []),
                "next_steps": claude_analysis.get("next_steps", []),
                "termination_reason": claude_analysis.get("termination_reason", "Standard completion")
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sub-agents', methods=['GET'])
def get_sub_agents():
    """Get all sub-agents."""
    try:
        agents = []
        for agent in sub_agent_manager.sub_agents.values():
            agents.append({
                "agent_id": agent.sub_agent_id,
                "patient_id": agent.patient_data.patient_id,
                "patient_name": agent.patient_data.name,
                "status": agent.status.value,
                "created_at": agent.created_at.isoformat(),
                "communication_count": len(agent.communication_results)
            })
        
        return jsonify({
            "success": True,
            "sub_agents": agents,
            "count": len(agents)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sub-agents/<agent_id>', methods=['GET'])
def get_sub_agent(agent_id):
    """Get a specific sub-agent."""
    try:
        if agent_id not in sub_agent_manager.sub_agents:
            return jsonify({"error": "Sub-agent not found"}), 404
        
        agent = sub_agent_manager.sub_agents[agent_id]
        return jsonify({
            "success": True,
            "sub_agent": {
                "agent_id": agent.sub_agent_id,
                "patient_id": agent.patient_data.patient_id,
                "patient_name": agent.patient_data.name,
                "status": agent.status.value,
                "created_at": agent.created_at.isoformat(),
                "communication_count": len(agent.communication_results),
                "latest_outcome": agent.communication_results[-1].outcome.value if agent.communication_results else None,
                "latest_confidence": agent.communication_results[-1].confidence_score if agent.communication_results else None
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    """Get system status."""
    try:
        status = sub_agent_manager.get_system_status()
        
        return jsonify({
            "success": True,
            "system_status": {
                "total_sub_agents": status['total_sub_agents'],
                "completed": status['completed'],
                "flagged_for_review": status['flagged_for_review'],
                "failed": status['failed'],
                "success_rate": status['success_rate']
            },
            "claude_status": {
                "available": llm_service.available,
                "provider": llm_service.provider.value if llm_service.provider else "unknown"
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo', methods=['POST'])
def run_demo():
    """Run a complete demo workflow."""
    try:
        data = request.get_json() or {}
        demo_type = data.get('type', 'full')
        
        if demo_type == 'full':
            # Full demo workflow
            # 1. Parse query
            query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
            parsed = run_async(master_agent.parse_doctor_query(query))
            
            # 2. Create sub-agents for diabetic patients
            diabetic_patients = [p for p in patients_db.values() if any("diabetes" in h.lower() for h in p.medical_history)]
            
            agents = []
            for patient in diabetic_patients:
                agent = run_async(sub_agent_manager.create_sub_agent(patient, parsed))
                agents.append(agent)
            
            # 3. Process communications
            results = []
            for agent in agents:
                result = run_async(agent.initiate_communication())
                results.append({
                    "agent_id": agent.sub_agent_id,
                    "patient_name": agent.patient_data.name,
                    "outcome": result.outcome.value,
                    "confidence": result.confidence_score,
                    "status": result.status.value
                })
            
            return jsonify({
                "success": True,
                "demo_type": "full",
                "query": query,
                "parsed_criteria": {
                    "action": parsed.action,
                    "time_filter": parsed.time_filter,
                    "condition_filter": parsed.condition_filter
                },
                "patients_processed": len(diabetic_patients),
                "results": results,
                "system_status": sub_agent_manager.get_system_status()
            })
        
        else:
            return jsonify({"error": "Unknown demo type"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Healthcare Agent Flask Server...")
    print("📡 API Documentation available at: http://localhost:8080/")
    print("🔧 Endpoints ready for testing!")
    app.run(debug=True, host='127.0.0.1', port=8080)
