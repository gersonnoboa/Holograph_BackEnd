import jsonpickle
import csv_handling
from datetime import datetime
import enums
import general_mining


def process_flow_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_variants(lst)
    info = mine_flow_info(mining)
    return jsonpickle.encode(info, unpicklable=False)

def mine_flow_info(lst):
    return []