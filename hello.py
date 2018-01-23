import os
from flask import Flask, request, redirect, url_for, jsonify
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
    return "Welcome to Python Flask App!"

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

@app.route("/active-time", methods=['POST'])
def get_active_time_info():
    print(request.form["parameters"]);
    return '{"message":"Active time not implemented yet"}'

@app.route("/traces", methods=['GET'])
def get_traces():
    #read_from_csv("data")
    return '{"message":"Traces not implemented yet"}'

@app.route("/file-headers", methods=['GET'])
def get_file_headers():
    return read_headers_from_csv("data")

def read_headers_from_csv(filename):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".csv"), 'r') as f:
        header = f.readline().strip()
        print(header)
        has_commas = "," in header
        split = header.split(",") if has_commas else header.split(";")
        return jsonify(split)

    # for idx, line in enumerate(f)
    #     line = line.strip()
    #     if len(line) == 0:
    #         continue

    #     parts = line.split(",")

    #     if idx == 1:
    #         lowercaseHeaders = [element.lower() for element in list]
    #         try:
    #             resourceIndex = lowercaseHeaders.index("resource")
    #         except ValueError:
    #             return '{"message":"error"}' 


if __name__ == "__main__":
    app.run(host='0.0.0.0')
