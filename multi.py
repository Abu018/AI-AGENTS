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

def process_pdf(pdf_path: str) -> Dict[str, Any]:
    """Processes the uploaded PDF using CrewAI."""
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        
        if not resume_text.strip():
            return {"error": "The uploaded PDF contains no text"}

        resume_analyzer = Agent(
            llm="gpt-4",
            role="Resume Analyst",
            goal="Extract key information such as experience, education, and skills in clear plain text format.",
            backstory="Expert HR professional with 10 years of experience analyzing resumes.",
            allow_delegation=False,
            verbose=True,
        )

        job_suitability_agent = Agent(
            llm="gpt-4", 
            role="Job Suitability Evaluator",
            goal="Identify the best job roles for the candidate and explain why in clear plain text.",
            backstory="Career advisor with deep expertise in job market trends.",
            allow_delegation=False,
            verbose=True,
        )

        extract_resume_task = Task(
            description=f"Extract key information from this resume:\n{resume_text}",
            expected_output="Clear plain text output with these sections:\n\nEXPERIENCE:\n- Bullet points of work experience\n\nEDUCATION:\n- Degrees and certifications\n\nSKILLS:\n- Technical and soft skills",
            agent=resume_analyzer,
        )

        job_suitability_task = Task(
            description="Analyze the resume content and recommend suitable job roles.",
            expected_output="Plain text output with:\n\nRECOMMENDED ROLES:\n- 3-5 job titles that match the candidate's profile\n\nEXPLANATION:\n- Brief reasoning for each recommendation",
            agent=job_suitability_agent,
        )

        crew = Crew(
            agents=[resume_analyzer, job_suitability_agent],
            tasks=[extract_resume_task, job_suitability_task],
            verbose=True
        )

        result = crew.kickoff()
        
        return {
            "status": "success",
            "analysis": str(result)  # Convert to plain string
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
            "result": result["analysis"]  # Plain text response
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)