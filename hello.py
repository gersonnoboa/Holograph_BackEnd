import os
from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
ALLOWED_EXTENSIONS = set(["csv", "xes", "mxml", "txt", "xml"])

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_filename(filename):
    return '.' in filename and get_extension(filename) in ALLOWED_EXTENSIONS
 
@app.route("/hello")
def hello():
    return "Welcome to Python Flask App!" + UPLOAD_FOLDER

@app.route("/upload", methods=['POST'])
def upload_file():
    if ('file' not in request.files):
        return 'No file has been uploaded'

    file = request.files['file']
    if file.filename == '':
        return 'No file has been uploaded'

    if file and allowed_filename(file.filename):        
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], "data." + get_extension(filename)))
        return 'File uploaded successfully'
    else:
        return 'Error uploading file' + str(file) + ' ' + str(allowed_filename(file.filename))

@app.route("/active-time", methods=['GET'])
def get_active_time_info():
    return 'Not implemented yet'

if __name__ == "__main__":
    app.run(host='0.0.0.0')