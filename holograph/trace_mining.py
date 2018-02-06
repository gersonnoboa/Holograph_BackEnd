import jsonpickle
import csv_handling
from datetime import datetime
import enums
import general_mining

def process_trace_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_variants(lst)
    #info = mine_trace_info(mining)
    return jsonpickle.encode(mining, unpicklable=False)


def mine_trace_info(lst):
    for variant in lst:
        resources = {event.resource for event in variant.cases}
        for resource in resources:
            #cases_with_resource = {case for case in variant.cases if }
            pass

def determine_resource_existence(resource, case):
    pass

class TraceVariant(general_mining.Variant):
    def __init__(self, activity_list, cases, resource):
        self.activity_list = activity_list
        self.cases = cases
        self.resource = resource
