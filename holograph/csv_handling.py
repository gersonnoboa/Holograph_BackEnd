from flask import jsonify

def read_headers_from_csv(filepath):
    with open(filepath, 'r') as f:
        header = f.readline().strip()
        split = split_csv_line(header)
        return jsonify(split)


def split_csv_line(line):
    has_commas = "," in line
    return line.split(",") if has_commas else line.split(";")
