import os
from werkzeug.utils import secure_filename
from flask import request

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_filename(filename, allowed_extensions):
    return '.' in filename and get_extension(filename) in allowed_extensions

def get_file_from_request(req):
    if 'file' not in req.files:
        return None

    file = req.files['file']
    return file

def save_file(file, folder, allowed_extensions):
    if file.filename == '':
        return False

    if file and allowed_filename(file.filename, allowed_extensions):
        filename = secure_filename(file.filename)
        file.save(os.path.join(folder, "data." + get_extension(filename)))
        return True
    else:
        return False
