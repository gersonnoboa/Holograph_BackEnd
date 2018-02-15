from flask import jsonify
from io import StringIO
import csv

def read_info_from_csv(filepath):
    info = []
    with open(filepath, 'r') as f:
        reader = get_csv_reader(f)
        info.append(next(reader))
        info.append(next(reader))
    return jsonify(info)


def get_csv_reader(f):
    dialect = csv.Sniffer().sniff(f.read())
    f.seek(0)
    reader = csv.reader(f, delimiter=dialect.delimiter)
    return reader
