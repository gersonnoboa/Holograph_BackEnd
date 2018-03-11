from flask import jsonify
from io import StringIO
import csv
import datetime

def read_info_from_csv(filepath):
    info = []
    print("%s: start reading info from csv" % datetime.datetime.now())
    with open(filepath, 'r') as f:
        reader = get_csv_reader(f)
        print("%s: reader obtained" % datetime.datetime.now())
        info.append(next(reader))
        print("%s: appending next 1" % datetime.datetime.now())
        info.append(next(reader))
        print("%s: appending next 2" % datetime.datetime.now())
    
    print("%s: returning" % datetime.datetime.now())
    return jsonify(info)


def get_csv_reader(f):
    print("%s: dialect" % datetime.datetime.now())
    dialect = csv.Sniffer().sniff(f.read())
    print("%s: seek to 0" % datetime.datetime.now())
    f.seek(0)
    print("%s: getting reader" % datetime.datetime.now())
    reader = csv.reader(f, delimiter=dialect.delimiter)
    return reader
