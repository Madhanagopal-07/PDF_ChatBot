from flask import Flask, render_template, request, flash, jsonify, session
import os
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from llm import vector_db,qa_chain
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Needed for session handling

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle PDF upload via AJAX
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        vector_db(file_path)
        
        # Store the PDF path in the session
        session['pdf_path'] = file_path

        return jsonify({'message': 'PDF uploaded successfully!'})
    
    return jsonify({'error': 'Allowed file types are pdf'}), 400

# Route to handle asking questions via AJAX
@app.route('/ask', methods=['POST'])
def ask_question():
    # Check if PDF is uploaded
    if 'pdf_path' not in session:
        return jsonify({'error': 'Please upload a PDF before asking questions.'}), 400

    # Load the PDF from the session
    file_path = session['pdf_path']
    '''
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    '''

    user_question = request.json.get('question')

    # Example logic to fetch answer from PDF based on user input
    try:
        result = qa_chain().invoke(user_question )['result']
    except (IndexError, ValueError):
        result = "Invalid question or page number. Please enter a valid page number."

    # Return the result as JSON
    return jsonify({'result': result, 'question': user_question})


@app.route('/clear', methods=['POST'])
def clear_all():
    session.pop('pdf_path', None)  
    return jsonify({'message': 'Session cleared'})

if __name__ == '__main__':
  
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
