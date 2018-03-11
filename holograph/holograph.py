from dateutil.parser import parse
from flask import Flask, request, redirect, url_for, jsonify, json
from flask_cors import CORS
import os
import file_handling
import csv_handling
import active_time_mining
import trace_mining
import flow_mining

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

    if file_saved_successfully is None:
        return "Error uploading file"

    return file_saved_successfully


@app.route("/active-time", methods=['GET'])
def get_active_time_info():
    filepath = get_filepath()
    return active_time_mining.process_active_time_info(request.args, filepath)


@app.route("/traces", methods=['GET'])
def get_traces():
    filepath = get_filepath()
    return trace_mining.process_trace_info(request.args, filepath)


@app.route("/flows", methods=['GET'])
def get_flows():
    filepath = get_filepath()
    return flow_mining.process_flow_info(request.args, filepath)


@app.route("/file-headers", methods=['GET'])
def get_file_headers():
    filepath = get_filepath()
    return csv_handling.read_info_from_csv(filepath)


def get_filepath():
    folder = app.config['UPLOAD_FOLDER']
    filename = request.args.get('fileID')
    filepath = os.path.join(folder, filename)
    return filepath


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run(threaded=True)
