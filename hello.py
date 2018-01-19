import os
from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = APP_ROOT
ALLOWED_EXTENSIONS = set(["csv", "xes", "mxml", "txt", "xml"])

def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
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
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'
    else:
        return 'Error uploading file' + str(file) + ' ' + str(allowed_filename(file.filename))
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')