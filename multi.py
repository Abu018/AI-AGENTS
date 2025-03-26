import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
from crewai import Crew, Task, Agent
from openai import OpenAI
from typing import Dict, Any
import json

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/upload": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OpenAI client
client = OpenAI(api_key="your-openai-api-key")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

def custom_serializer(obj):
    """Custom JSON serializer for objects not serializable by default."""
    if hasattr(obj, 'dict'):  # For CrewAI objects with .dict() method
        return obj.dict()
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

def process_pdf(pdf_path: str) -> Dict[str, Any]:
    """Processes the uploaded PDF using CrewAI."""
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        
        if not resume_text.strip():
            return {"error": "The uploaded PDF contains no text"}

        resume_analyzer = Agent(
            llm="gpt-4",
            role="Resume Analyst",
            goal="Extract key information such as experience, education, and skills.",
            backstory="Expert HR professional.",
            allow_delegation=False,
            verbose=True,
        )

        job_suitability_agent = Agent(
            llm="gpt-4",
            role="Job Suitability Evaluator", 
            goal="Identify the best job roles for the candidate.",
            backstory="Career advisor with deep expertise.",
            allow_delegation=False,
            verbose=True,
        )

        extract_resume_task = Task(
            description=f"Extract key information from the resume:\n{resume_text}",
            expected_output="A structured summary of the resume.",
            agent=resume_analyzer,
        )

        job_suitability_task = Task(
            description="Determine the most suitable job roles based on resume contents.",
            expected_output="A job recommendation report.",
            agent=job_suitability_agent,
        )

        crew = Crew(
            agents=[resume_analyzer, job_suitability_agent],
            tasks=[extract_resume_task, job_suitability_task],
            verbose=True
        )

        result = crew.kickoff()
        
        # Use custom serialization
        serialized_result = json.loads(json.dumps(result, default=custom_serializer))
        
        return {
            "status": "success",
            "analysis": serialized_result
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles PDF upload and processing."""
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["pdf"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if not (file and file.filename.lower().endswith('.pdf')):
            return jsonify({"error": "Invalid file format"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        result = process_pdf(file_path)
        
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

        if "error" in result:
            return jsonify(result), 400
            
        return jsonify({
            "status": "success",
            "filename": file.filename,
            "result": result["analysis"]
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)