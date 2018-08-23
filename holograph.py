from dateutil.parser import parse
from flask import Flask, request, redirect, url_for, jsonify, json
from flask_cors import CORS, cross_origin
import os
import file_handling
import csv_handling
import active_time_mining
import trace_mining
import flow_mining
import individual_mining
import group_mining

app = Flask(__name__)
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
app.config['CORS_HEADERS'] = 'Content-Type'

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
    return active_time_mining.process_active_time_info(request.args, get_filepath())


@app.route("/traces", methods=['GET'])
def get_traces():
    return trace_mining.process_trace_info(request.args, get_filepath())


@app.route("/flows", methods=['GET'])
def get_flows():
    return flow_mining.process_flow_info(request.args, get_filepath())


@app.route("/individual", methods=['GET'])
def get_individual():
    return individual_mining.process_individual_info(request.args, get_filepath())


@app.route("/group-activity", methods=['GET'])
def get_group_activity():
    return group_mining.process_group_activity_info(request.args, get_filepath())

@app.route("/group-resource", methods=['GET'])
@cross_origin()
def get_group_resource():
    return group_mining.process_group_resource_info(request.args, get_filepath())


@app.route("/file-headers", methods=['GET'])
def get_file_headers():
    filepath = get_filepath()
    return csv_handling.read_info_from_csv(filepath)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers',
                       'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods',
                       'GET,PUT,POST,DELETE,OPTIONS')
  return response


def get_filepath():
    folder = app.config['UPLOAD_FOLDER']
    filename = request.args.get('fileID')
    filepath = os.path.join(folder, filename)
    return filepath


if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run()
