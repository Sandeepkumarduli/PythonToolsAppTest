import os
import logging
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
from server.tools.pdf_to_docx import convert_pdf_to_docx
from server.tools.docx_to_pdf import convert_docx_to_pdf
from server.tools.word_counter import count_words

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__, static_folder='client', static_url_path='')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate unique filename to avoid conflicts"""
    name, ext = os.path.splitext(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{ext}"

# Routes for serving HTML pages
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/pricing')
def pricing():
    return app.send_static_file('pricing.html')

@app.route('/login')
def login():
    return app.send_static_file('login.html')

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    return app.send_static_file(f'tools/{tool_name}.html')

# API Routes
@app.route('/api/convert/pdf-to-docx', methods=['POST'])
def api_pdf_to_docx():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_path)
        
        # Convert file
        output_filename = unique_filename.rsplit('.', 1)[0] + '.docx'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        success, message = convert_pdf_to_docx(input_path, output_path)
        
        if success:
            return jsonify({
                'success': True, 
                'download_url': f'/api/download/{output_filename}',
                'filename': output_filename
            })
        else:
            # Clean up input file on failure
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logging.error(f"Error in PDF to DOCX conversion: {str(e)}")
        return jsonify({'error': 'An error occurred during conversion'}), 500

@app.route('/api/convert/docx-to-pdf', methods=['POST'])
def api_docx_to_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only DOCX files are allowed.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_path)
        
        # Convert file
        output_filename = unique_filename.rsplit('.', 1)[0] + '.pdf'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        success, message = convert_docx_to_pdf(input_path, output_path)
        
        if success:
            return jsonify({
                'success': True, 
                'download_url': f'/api/download/{output_filename}',
                'filename': output_filename
            })
        else:
            # Clean up input file on failure
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logging.error(f"Error in DOCX to PDF conversion: {str(e)}")
        return jsonify({'error': 'An error occurred during conversion'}), 500

@app.route('/api/word-count', methods=['POST'])
def api_word_count():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        word_count_data = count_words(text)
        
        return jsonify({
            'success': True,
            'data': word_count_data
        })
        
    except Exception as e:
        logging.error(f"Error in word counting: {str(e)}")
        return jsonify({'error': 'An error occurred during word counting'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'An error occurred during download'}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500
