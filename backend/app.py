from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from downloader import download_materials, get_semesters, get_modules
import os

app = Flask(__name__)
CORS(app)

# Create an absolute path for downloads that won't be affected by working directory
DOWNLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'downloads'))
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    module_url = data.get('module_url')

    try:
        msg = download_materials(username, password, module_url, DOWNLOAD_FOLDER)
        return msg
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        semesters = get_semesters(username, password)
        return jsonify({"success": True, "semesters": semesters})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/modules', methods=['POST'])
def get_course_modules():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    semester_id = data.get('semester_id')
    
    try:
        modules = get_modules(username, password, semester_id)
        return jsonify({"success": True, "modules": modules})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Add a route to serve downloaded files
@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Turn off the reloader to prevent interruption during Playwright operations
    app.run(debug=True, use_reloader=False)