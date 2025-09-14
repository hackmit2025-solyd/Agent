"""
Healthcare Agent Flask Server
RESTful API for the LLM-powered healthcare agent system.
"""
from flask import Flask, request, jsonify, Response
import asyncio
import json
import time
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from agents.master_agent import MasterAgent, PatientRecord, ParsedCriteria
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from services.llm_service import llm_service

# Load environment variables from .env file
load_dotenv()

# Debug: Check if Claude API key is loaded
claude_secret = os.getenv("CLAUDE_SECRET")
if claude_secret and claude_secret != "your-claude-api-key-here":
    print(f"✅ Claude API key loaded: {claude_secret[:10]}...")
else:
    print("❌ Claude API key not found in environment")

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

@app.route('/api/doctor-query', methods=['POST'])
def process_doctor_query():
    """Complete flow: Doctor Query → Master Agent → Database → Sub-Agents → Communication."""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "query is required"}), 400
        
        doctor_query = data['query']
        
        # Step 1: Master Agent parses doctor query
        print(f"🧠 Master Agent parsing: '{doctor_query}'")
        parsed_criteria = run_async(master_agent.parse_doctor_query(doctor_query))
        
        # Step 2: Master Agent queries database server with original query
        print(f"📊 Querying database with original query: '{doctor_query}'")
        patient_records = run_async(master_agent.query_database(parsed_criteria, doctor_query))
        
        # Step 3: Create sub-agents for each patient
        print(f"🤖 Creating {len(patient_records)} sub-agents...")
        created_agents = []
        
        for patient_record in patient_records:
            # Create sub-agent
            sub_agent_data = {
                "patient_id": patient_record.patient_id,
                "context": {
                    "action": parsed_criteria.action,
                    "time_filter": parsed_criteria.time_filter,
                    "condition_filter": parsed_criteria.condition_filter,
                    "symptom_filter": parsed_criteria.symptom_filter,
                    "age_filter": parsed_criteria.age_filter,
                    "medication_filter": parsed_criteria.medication_filter,
                    "patient_criteria": parsed_criteria.patient_criteria
                }
            }
            
            # Create sub-agent using existing endpoint logic
            sub_agent = SubAgent(
                patient_data=patient_record,
                master_context=parsed_criteria,
                sub_agent_id=f"sub_agent_{patient_record.patient_id}_{int(time.time())}"
            )
            
            sub_agent_manager.sub_agents[sub_agent.sub_agent_id] = sub_agent
            created_agents.append({
                "agent_id": sub_agent.sub_agent_id,
                "patient_name": patient_record.name,
                "patient_id": patient_record.patient_id,
                "medical_history": patient_record.medical_history
            })
        
        return jsonify({
            "success": True,
            "doctor_query": doctor_query,
            "parsed_criteria": {
                "action": parsed_criteria.action,
                "time_filter": parsed_criteria.time_filter,
                "condition_filter": parsed_criteria.condition_filter,
                "symptom_filter": parsed_criteria.symptom_filter,
                "age_filter": parsed_criteria.age_filter,
                "medication_filter": parsed_criteria.medication_filter,
                "patient_criteria": parsed_criteria.patient_criteria
            },
            "patients_found": len(patient_records),
            "sub_agents_created": len(created_agents),
            "sub_agents": created_agents,
            "next_step": "Use /api/conversation/start to begin patient communications"
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

@app.route('/api/healthcare-query', methods=['GET'])
def healthcare_query_get():
    """
    GET endpoint for frontend integration with live streaming
    Query parameter: query (doctor's query)
    Returns: Live stream of processing state
    """
    try:
        # Get query from URL parameters
        doctor_query = request.args.get('query', '')
        if not doctor_query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        print(f"🌐 Frontend Query: '{doctor_query}'")
        
        # Create a response generator for streaming
        def generate_response():
            yield f"data: {json.dumps({'status': 'started', 'message': 'Processing doctor query...'})}\n\n"
            
            # Step 1: Parse doctor query
            yield f"data: {json.dumps({'status': 'parsing', 'message': 'Parsing doctor query with AI...'})}\n\n"
            parsed_criteria = asyncio.run(master_agent.parse_doctor_query(doctor_query))
            yield f"data: {json.dumps({'status': 'parsed', 'message': f'Query parsed: {parsed_criteria.action}', 'criteria': parsed_criteria.__dict__})}\n\n"
            
            # Step 2: Query database
            yield f"data: {json.dumps({'status': 'database', 'message': 'Querying database for patients...'})}\n\n"
            patients = asyncio.run(master_agent.query_database(parsed_criteria, original_query=doctor_query))
            yield f"data: {json.dumps({'status': 'database_found', 'message': f'Found {len(patients)} patients', 'patients': [p.__dict__ for p in patients]})}\n\n"
            
            # Step 3: Create sub-agents and start conversations
            yield f"data: {json.dumps({'status': 'creating_agents', 'message': 'Creating sub-agents for each patient...'})}\n\n"
            sub_agents_created = []
            
            for i, patient in enumerate(patients):
                sub_agent = SubAgent(
                    patient_data=patient,
                    master_context=parsed_criteria,
                    sub_agent_id=f"sub_agent_{patient.patient_id}_{int(time.time())}"
                )
                sub_agent_manager.sub_agents[sub_agent.sub_agent_id] = sub_agent
                sub_agents_created.append({
                    'agent_id': sub_agent.sub_agent_id,
                    'patient_name': patient.name,
                    'medical_history': patient.medical_history,
                    'status': 'created'
                })
                yield f"data: {json.dumps({'status': 'agent_created', 'message': f'Created agent for {patient.name}', 'agent_id': sub_agent.sub_agent_id})}\n\n"
                
                # Start conversation automatically
                yield f"data: {json.dumps({'status': 'starting_chat', 'message': f'Starting conversation with {patient.name}...', 'agent_id': sub_agent.sub_agent_id})}\n\n"
                
                try:
                    # Get initial agent message
                    response = requests.post(f"http://localhost:8080/api/conversation/start", 
                                           json={"agent_id": sub_agent.sub_agent_id})
                    if response.status_code == 200:
                        data = response.json()
                        agent_message = data.get('agent_message', 'Hello!')
                        yield f"data: {json.dumps({'status': 'agent_message', 'message': agent_message, 'agent_id': sub_agent.sub_agent_id, 'patient_name': patient.name})}\n\n"
                        
                        # Simulate patient responses for demo
                        patient_responses = [
                            "Hi, I'm doing okay. I've been having some issues with my vision lately.",
                            "Yes, I'm still taking my medications as prescribed.",
                            "The vision problems seem to be getting worse, especially at night.",
                            "I'm worried about my diabetes control. My blood sugar has been high."
                        ]
                        
                        for round_num, patient_msg in enumerate(patient_responses, 1):
                            yield f"data: {json.dumps({'status': 'patient_message', 'message': patient_msg, 'agent_id': sub_agent.sub_agent_id, 'round': round_num})}\n\n"
                            
                            # Get agent response
                            response = requests.post(f"http://localhost:8080/api/conversation/respond",
                                                   json={
                                                       "agent_id": sub_agent.sub_agent_id,
                                                       "patient_message": patient_msg
                                                   })
                            
                            if response.status_code == 200:
                                data = response.json()
                                agent_response = data.get('agent_message', 'I understand.')
                                should_terminate = data.get('should_terminate', False)
                                termination_reason = data.get('termination_reason', '')
                                
                                yield f"data: {json.dumps({'status': 'agent_response', 'message': agent_response, 'agent_id': sub_agent.sub_agent_id, 'round': round_num})}\n\n"
                                
                                if should_terminate:
                                    yield f"data: {json.dumps({'status': 'conversation_ended', 'message': f'Conversation ended: {termination_reason}', 'agent_id': sub_agent.sub_agent_id})}\n\n"
                                    break
                            else:
                                yield f"data: {json.dumps({'status': 'error', 'message': f'Error getting agent response: {response.status_code}', 'agent_id': sub_agent.sub_agent_id})}\n\n"
                                break
                            
                            # Small delay between messages
                            time.sleep(1)
                    else:
                        yield f"data: {json.dumps({'status': 'error', 'message': f'Error starting conversation: {response.status_code}', 'agent_id': sub_agent.sub_agent_id})}\n\n"
                        
                except Exception as e:
                    yield f"data: {json.dumps({'status': 'error', 'message': f'Error in conversation: {str(e)}', 'agent_id': sub_agent.sub_agent_id})}\n\n"
            
            # Step 4: Final result
            yield f"data: {json.dumps({'status': 'completed', 'message': 'All sub-agents created successfully', 'total_agents': len(sub_agents_created), 'agents': sub_agents_created})}\n\n"
            
            # Final completion
            yield f"data: {json.dumps({'status': 'done', 'message': 'Processing complete'})}\n\n"
        
        return Response(generate_response(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"❌ Error in healthcare query: {e}")
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

@app.route('/api/conversation/start', methods=['POST'])
def start_conversation():
    """Start an interactive conversation with a sub-agent."""
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
        
        # Initialize conversation state
        if not hasattr(sub_agent, 'conversation_state'):
            sub_agent.conversation_state = {
                "rounds": 0,
                "max_rounds": 5,
                "history": [],
                "terminated": False
            }
        
        # Reset conversation if starting fresh
        sub_agent.conversation_state["rounds"] = 0
        sub_agent.conversation_state["history"] = []
        sub_agent.conversation_state["terminated"] = False
        
        # Generate initial agent message using Claude
        patient_data = {
            "name": sub_agent.patient_data.name,
            "medical_history": sub_agent.patient_data.medical_history,
            "current_medications": sub_agent.patient_data.current_medications,
            "symptoms": sub_agent.patient_data.symptoms or []
        }
        
        # Use Claude to generate the initial conversation starter
        initial_message = run_async(llm_service.generate_conversation_starter(patient_data, sub_agent.master_context))
        
        # Add to conversation history
        sub_agent.conversation_state["history"].append({
            "speaker": "agent",
            "message": initial_message,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "success": True,
            "agent_message": initial_message,
            "conversation_id": agent_id,
            "max_rounds": sub_agent.conversation_state["max_rounds"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversation/respond', methods=['POST'])
def respond_to_conversation():
    """Respond to a conversation with the sub-agent."""
    try:
        data = request.get_json()
        if not data or 'agent_id' not in data or 'patient_message' not in data:
            return jsonify({"error": "agent_id and patient_message are required"}), 400
        
        agent_id = data['agent_id']
        patient_message = data['patient_message']
        
        # Find sub-agent
        sub_agent = None
        for agent in sub_agent_manager.sub_agents.values():
            if agent.sub_agent_id == agent_id:
                sub_agent = agent
                break
        
        if not sub_agent:
            return jsonify({"error": "Sub-agent not found"}), 404
        
        if not hasattr(sub_agent, 'conversation_state'):
            return jsonify({"error": "No active conversation. Start a conversation first."}), 400
        
        if sub_agent.conversation_state["terminated"]:
            return jsonify({"error": "Conversation has been terminated."}), 400
        
        # Add patient message to history
        sub_agent.conversation_state["history"].append({
            "speaker": "patient",
            "message": patient_message,
            "timestamp": datetime.now().isoformat()
        })
        
        sub_agent.conversation_state["rounds"] += 1
        
        # Use Claude to generate response and decide if conversation should continue
        patient_data = {
            "name": sub_agent.patient_data.name,
            "medical_history": sub_agent.patient_data.medical_history,
            "current_medications": sub_agent.patient_data.current_medications,
            "symptoms": sub_agent.patient_data.symptoms or []
        }
        
        claude_response = run_async(llm_service.generate_conversation_response(
            patient_message, 
            sub_agent.conversation_state["history"], 
            patient_data, 
            sub_agent.master_context,
            sub_agent.conversation_state["rounds"]
        ))
        
        agent_response = claude_response.get("response", "Thank you for that information.")
        should_terminate = claude_response.get("should_terminate", False)
        termination_reason = claude_response.get("termination_reason", "")
        
        # Check if Claude wants to terminate the conversation
        if should_terminate or sub_agent.conversation_state["rounds"] >= sub_agent.conversation_state["max_rounds"]:
            # Terminate conversation
            sub_agent.conversation_state["terminated"] = True
            
            if should_terminate and termination_reason:
                agent_response = f"{agent_response} {termination_reason}"
            else:
                agent_response = "Thank you for your time today. I have enough information to complete your follow-up. Let me process this and get back to you with next steps."
            
            sub_agent.conversation_state["history"].append({
                "speaker": "agent",
                "message": agent_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process the complete conversation
            conversation_result = process_complete_conversation(sub_agent)
            
            return jsonify({
                "success": True,
                "agent_message": agent_response,
                "conversation_terminated": True,
                "conversation_result": conversation_result,
                "termination_reason": termination_reason
            })
        
        # Add agent response to history
        sub_agent.conversation_state["history"].append({
            "speaker": "agent",
            "message": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "success": True,
            "agent_message": agent_response,
            "conversation_round": sub_agent.conversation_state["rounds"],
            "max_rounds": sub_agent.conversation_state["max_rounds"],
            "conversation_terminated": False
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_agent_response(patient_message, conversation_round):
    """Generate intelligent agent response based on patient input and conversation progress."""
    patient_msg_lower = patient_message.lower()
    
    # Check for termination signals
    if "nope" in patient_msg_lower or "nothing" in patient_msg_lower or "no" in patient_msg_lower:
        if conversation_round >= 3:
            return "I understand. Based on our conversation, it sounds like you're managing well. Let me wrap up this follow-up call."
        else:
            return "That's good to know. Any other concerns or symptoms you'd like to discuss?"
    
    # Context-aware responses
    if "headache" in patient_msg_lower or "head" in patient_msg_lower:
        if "not too bad" in patient_msg_lower or "mild" in patient_msg_lower:
            return "I understand the headaches are mild. Are you taking any pain medication for them? Any other symptoms I should know about?"
        else:
            return "I understand you're experiencing headaches. Can you tell me more about the frequency and intensity? Are they new or have you had them before?"
    elif "good" in patient_msg_lower or "fine" in patient_msg_lower or "well" in patient_msg_lower:
        return "That's great to hear! Are you taking your medications as prescribed? Any side effects to report?"
    elif "help" in patient_msg_lower:
        return "I'm here to help! What specific concerns do you have about your health? Please share any symptoms or issues you're experiencing."
    elif "pain" in patient_msg_lower or "hurt" in patient_msg_lower:
        return "I'm sorry to hear you're in pain. Can you describe the pain - where is it located and what does it feel like?"
    elif "medication" in patient_msg_lower or "medicine" in patient_msg_lower:
        return "Let's talk about your medications. Are you taking them as prescribed? Any difficulties or concerns with your current medication regimen?"
    else:
        return "Thank you for sharing that. Can you tell me more about how you've been managing your condition? Any new symptoms or changes you've noticed?"

def process_complete_conversation(sub_agent):
    """Process a complete conversation and make a decision."""
    try:
        # Analyze conversation to create realistic communication data
        patient_messages = [msg['message'].lower() for msg in sub_agent.conversation_state["history"] if msg['speaker'] == 'patient']
        all_text = ' '.join(patient_messages)
        
        # Determine data quality based on conversation
        has_symptoms = any(word in all_text for word in ['headache', 'pain', 'hurt', 'symptom', 'problem'])
        has_medication_info = any(word in all_text for word in ['medication', 'medicine', 'pill', 'drug', 'taking'])
        patient_responsive = len(patient_messages) > 0
        conversation_complete = sub_agent.conversation_state["rounds"] >= 3
        
        # Create communication data from conversation
        communication_data = {
            "session_id": f"conversation_{sub_agent.sub_agent_id}",
            "duration": len(sub_agent.conversation_state["history"]) * 30.0,
            "confidence_score": 0.85 if conversation_complete else 0.60,
            "conversation_quality": "excellent" if conversation_complete else "good",
            "data_obtained": {
                "patient_responsiveness": patient_responsive,
                "symptom_information": has_symptoms,
                "medication_adherence": has_medication_info,
                "overall_wellbeing": "discussed" if conversation_complete else "partial"
            },
            "missing_data": [] if conversation_complete else ["detailed_symptom_description", "medication_adherence"],
            "transcript": "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in sub_agent.conversation_state["history"]])
        }
        
        # Let Claude analyze the communication
        patient_data = {
            "name": sub_agent.patient_data.name,
            "medical_history": sub_agent.patient_data.medical_history,
            "current_medications": sub_agent.patient_data.current_medications,
            "symptoms": sub_agent.patient_data.symptoms or []
        }
        
        claude_analysis = run_async(llm_service.analyze_communication_outcome(communication_data, patient_data))
        
        # Convert Claude's analysis to our decision outcome
        outcome_str = claude_analysis.get("outcome", "close_loop").lower()
        decision_outcome = DecisionOutcome(outcome_str) if outcome_str in [o.value for o in DecisionOutcome] else DecisionOutcome.CLOSE_LOOP
        
        # Create communication result
        communication_result = {
            "agent_id": sub_agent.sub_agent_id,
            "patient_name": sub_agent.patient_data.name,
            "outcome": decision_outcome.value,
            "confidence": claude_analysis.get("confidence", 0.8),
            "reasoning": claude_analysis.get("reasoning", "Communication processed successfully"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update sub-agent status
        sub_agent.status = FollowUpStatus.COMPLETED if decision_outcome == DecisionOutcome.CLOSE_LOOP else FollowUpStatus.FLAGGED_FOR_REVIEW
        sub_agent.communication_results.append(communication_result)
        
        return communication_result
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    # Get port from environment (Railway sets this)
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting Healthcare Agent Flask Server...")
    print(f"📡 API Documentation available at: http://{host}:{port}/")
    print("🔧 Endpoints ready for testing!")
    print(f"🌍 Environment: {'Development' if debug else 'Production'}")
    
    app.run(debug=debug, host=host, port=port)
