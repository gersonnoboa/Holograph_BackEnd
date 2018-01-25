from dateutil.parser import parse
from flask import Flask, request, redirect, url_for, jsonify, json
from flask_cors import CORS
import os
import file_handling
import csv_handling
import active_time_mining

app = Flask(__name__)
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH

@app.route("/hello")
def hello():
    return "Welcome to Python Flask App!"


@app.route("/upload", methods=['POST'])
def upload_file():
    allowed_extensions = set(["csv", "xes", "mxml", "txt", "xml"])
    file = file_handling.get_file_from_request(request)
    if file is None:
        return "Error uploading file"

    folder = app.config['UPLOAD_FOLDER']
    file_saved_successfully = file_handling.save_file(file, folder, allowed_extensions)

    if not file_saved_successfully:
        return "Error uploading file"

    return "File uploaded successfully"


@app.route("/active-time", methods=['POST'])
def get_active_time_info():
    folder = app.config['UPLOAD_FOLDER']
    filename = "data.csv"
    filepath = os.path.join(folder, filename)
    return active_time_mining.process_active_time_info(request.get_json(force=True), filepath)


@app.route("/traces", methods=['GET'])
def get_traces():
    #read_from_csv("data")
    return '{"message":"Traces not implemented yet"}'


@app.route("/file-headers", methods=['GET'])
def get_file_headers():
    folder = app.config['UPLOAD_FOLDER']
    filename = "data.csv"
    filepath = os.path.join(folder, filename)
    return csv_handling.read_headers_from_csv(filepath)


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run()
