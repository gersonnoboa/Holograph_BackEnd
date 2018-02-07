from flask import jsonify
from io import StringIO
import csv

def read_line_from_csv(f):
    header = f.readline().strip()
    split = split_csv_line(header)
    return split

def read_headers_and_first_row_from_csv(filepath):
    info = []
    with open(filepath, 'r') as f:
        info.append(read_line_from_csv(f))
        info.append(read_line_from_csv(f))
    f.close()
    return jsonify(info)

def read_info_from_csv(filepath):
    info = []
    with open(filepath, 'r') as f:
        dialect = csv.Sniffer().sniff(f.read())
        f.seek(0)
        reader = csv.reader(f, delimiter=dialect.delimiter)
        info.append(next(reader))
        info.append(next(reader))
    return jsonify(info)

def split_csv_line(line):
    has_commas = "," in line
    return line.split(",") if has_commas else line.split(";")
