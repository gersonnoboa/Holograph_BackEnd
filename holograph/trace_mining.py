import jsonpickle
import csv_handling
from datetime import datetime
import enums
import general_mining

def process_trace_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_variants(lst)
    return jsonpickle.encode(mining, unpicklable=False)


def mine_trace_info(lst):
    for variant in lst:
        pass


class TraceVariant(general_mining.Variant):
    def __init__(self, activity_list, cases, resource):
        self.activity_list = activity_list
        self.cases = cases
        self.resource = resource
