import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import vision
import fitz  # PyMuPDF library
from PIL import Image
import io

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- AI Configuration ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
vision_client = vision.ImageAnnotatorClient()

# --- Helper Function for Gemini AI ---
def generate_analysis_from_file(file_content, file_type, language):
    """
    Analyzes content from a file (image or PDF) using a multi-modal Gemini model.
    """
    # This is the correct prompt for a multi-modal request
    prompt = f"""
    You are an expert at analyzing and simplifying complex Indian government documents.
    First, perform OCR to extract all text from the document image(s) provided.
    Then, based on the extracted text, provide the following in simple, clear {language}:

    1.  **Document Legitimacy:** Based on the formatting, language, and structure, provide a legitimacy analysis. Start with a verdict: "Likely Legitimate" or "Potential Red Flags Found". Then, give a one-sentence reason for your verdict.
    2.  **Main Purpose:** In one simple sentence, what is the main purpose of this document?
    3.  **Key Points:** In a bulleted list, what are the key benefits, rules, or information for a citizen?
    4.  **Action Items:** In a clear list, what, if any, actions are required from the citizen, including deadlines?
    """

    file_parts = []
    
    if file_type == 'pdf':
        # Convert PDF pages to image objects
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        for page in pdf_document:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_bytes))
            file_parts.append(pil_image)
        pdf_document.close()
    else: # It's an image
        pil_image = Image.open(io.BytesIO(file_content))
        file_parts.append(pil_image)

    # Combine the text prompt and the image parts for the request
    request_payload = [prompt] + file_parts
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(request_payload)
    return response.text
# --- Main API Endpoint ---
@app.route('/simplify', methods=['POST'])
def simplify_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'English')

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    file_content = file.read()
    file_type = 'pdf' if file.filename.lower().endswith('.pdf') else 'image'

    # This single call does everything: OCR, analysis, and summarization
    simplified_text = generate_analysis_from_file(file_content, file_type, language)

    # Check if the helper function returned an error
    if simplified_text.strip().startswith("Error:"):
        return jsonify({"error": simplified_text.replace('Error: ', '')}), 500

    return jsonify({
        "simplified_text": simplified_text
    })


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signin_page():
    # You would create a signin.html file in your templates folder
    return render_template('signup.html')

@app.route('/start')
def start_page():
    # This tells Flask to find and show a file named start.html
    return render_template('start.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(debug=True)