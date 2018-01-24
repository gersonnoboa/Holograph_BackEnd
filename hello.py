import os
from enum import Enum
from datetime import datetime
from dateutil.parser import parse
from flask import Flask, request, redirect, url_for, jsonify, json
from flask_cors import CORS
from werkzeug.utils import secure_filename
import jsonpickle

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
    return process_active_time_info()
    

def process_active_time_info():
    json_from_request = request.get_json(force=True)
    resource = str(json_from_request["resource"])
    activity = str(json_from_request["activity"])
    log_type = str(json_from_request["type"])
    parameter_one = str(json_from_request["parameterOne"])
    parameter_two = str(json_from_request["parameterTwo"])
    
    idx_resource = 0
    idx_activity = 0
    idx_parameter_one = 0
    idx_parameter_two = 0

    list = []

    with open(os.path.join(app.config['UPLOAD_FOLDER'], "data.csv"), 'r') as f:
        for idx, line in enumerate(f):
            line = line.strip()

            if len(line) == 0:
                continue

            split = split_csv_line(line)

            if idx == 0:
                idx_resource = split.index(resource)
                idx_activity = split.index(activity)
                idx_parameter_one = split.index(parameter_one)
                if (log_type == LogType.StartAndEndDate.value):
                    idx_parameter_two = split.index(parameter_two)
            else:
                res = split[idx_resource]
                act = split[idx_activity]
                if (log_type == LogType.StartAndEndDate.value):
                    start_date = datetime.strptime(split[idx_parameter_one], '%d-%m-%Y:%H.%M')
                    end_date = datetime.strptime(split[idx_parameter_two], '%d-%m-%Y:%H.%M')
                    event = ActiveTimeEvent(res, act, start_date, end_date)
                    list.append(event)
    
    mining = mine_active_time_info(list)
    return jsonpickle.encode(mining, unpicklable=False)

def mine_active_time_info(list):
    activities = {event.activity for event in list}

    list_activities = []
    for activity in activities:
        all_events_for_activity = [event for event in list if event.activity == activity]
        resources = {event.resource for event in all_events_for_activity}
        list_resources = []
        for resource in resources:
            all_events_for_resource = [event for event in all_events_for_activity if event.resource == resource]
            total_active_time = sum([e.subtract_dates() for e in all_events_for_resource])
            list_resources.append(Resource(resource, total_active_time))
        
        list_activities.append(Activity(activity, list_resources))
    
    return list_activities

class Activity:
    def __init__(self, activity, resources):
        self.activity = activity
        self.resources = resources

class Resource:
    def __init__(self, resource, active_time):
        self.resource = resource
        self.active_time = active_time

class ActiveTimeEvent:
    def __init__(self, resource, activity, start_date, end_date):
        self.resource = resource
        self.activity = activity
        self.start_date = start_date
        self.end_date = end_date

    def subtract_dates(self):
        return (self.end_date - self.start_date).seconds

class LogType(Enum):
    ActiveTime = "Has active time only"
    StartAndEndDate = "Has start and end date"
    Timestamp = "Has timestamp only"

@app.route("/traces", methods=['GET'])
def get_traces():
    #read_from_csv("data")
    return '{"message":"Traces not implemented yet"}'

@app.route("/file-headers", methods=['GET'])
def get_file_headers():
    return read_headers_from_csv()

def read_headers_from_csv():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], "data.csv"), 'r') as f:
        header = f.readline().strip()
        split = split_csv_line(header)
        return jsonify(split)

def split_csv_line(line):
    has_commas = "," in line
    return line.split(",") if has_commas else line.split(";")

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run()
