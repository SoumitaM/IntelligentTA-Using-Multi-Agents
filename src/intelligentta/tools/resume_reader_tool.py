import os
import PyPDF2
import glob
from crewai import Tool

def read_resume(file_path: str) -> str:
    """
    Extracts text from a resume PDF file
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the resume
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            return text
    except Exception as e:
        return f"Error reading resume: {str(e)}"

def list_resumes(resume_folder: str = "resumes") -> str:
    """
    Lists all available resume files in the resumes folder
    
    Args:
        resume_folder (str): Path to the folder containing resumes (default: "resumes")
        
    Returns:
        str: List of resume file paths
    """
    try:
        if not os.path.exists(resume_folder):
            return f"Resume folder '{resume_folder}' not found"
        
        resume_files = glob.glob(os.path.join(resume_folder, "*.pdf"))
        if not resume_files:
            return f"No resume PDFs found in '{resume_folder}'"
        
        return "\n".join(resume_files)
    except Exception as e:
        return f"Error listing resumes: {str(e)}"

# Create tools using Tool class from crewai
read_resume_tool = Tool(
    name="read_resume",
    description="Extracts text from a resume PDF file",
    func=read_resume
)

list_resumes_tool = Tool(
    name="list_resumes", 
    description="Lists all available resume files in the resumes folder",
    func=list_resumes
)
