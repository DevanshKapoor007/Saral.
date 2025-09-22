import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import vision
import fitz  # PyMuPDF library

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- AI Configuration ---
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)
vision_client = vision.ImageAnnotatorClient()

# --- Helper Function for Gemini AI ---
def get_gemini_summary(text_content, language):
    """Gets the simplified summary from the Gemini API."""
    prompt = f"""
    You are an expert at simplifying complex Indian government documents for a common citizen. 
    Analyze the following text extracted from a government document. Your entire response must be in simple, clear {language}.

    1.  **Main Purpose:** In one simple sentence, what is the main purpose of this document?
    2.  **Key Points:** In simple bullet points, list the key benefits, rules, or information for the citizen.
    3.  **Action Items:** Create a clear 'What you need to do' list with any required actions or deadlines. If there are no actions, state that clearly.

    ---DOCUMENT TEXT---
    {text_content}
    ---END OF TEXT---
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
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

    extracted_text = ""
    # --- NEW: Check file type and process accordingly ---
    if file.filename.lower().endswith('.pdf'):
        try:
            print("Processing PDF file...")
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            for page in pdf_document:
                extracted_text += page.get_text()
            pdf_document.close()
            print("Successfully extracted text from PDF.")
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return jsonify({"error": "Could not process the PDF file"}), 500
    else: # Assume it's an image
        try:
            print("Processing image file...")
            image_content = file.read()
            image = vision.Image(content=image_content)
            
            response = vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                extracted_text = texts[0].description
                print("Successfully extracted text from image.")
            else:
                print("No text found in the image.")
                return jsonify({"error": "Could not extract text from the image"}), 400
        except Exception as e:
            print(f"Error processing image: {e}")
            return jsonify({"error": "Could not process the image file"}), 500

    if extracted_text:
        print(f"Sending extracted text to Gemini API for simplification in {language}...")
        simplified_text = get_gemini_summary(extracted_text, language)
        print("Successfully received summary from Gemini.")
        
        return jsonify({
            "original_text": extracted_text,
            "simplified_text": simplified_text
        })
    else:
        return jsonify({"error": "Could not extract any text from the file"}), 400


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