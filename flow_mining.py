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
    filtered_list = list(variant for variant in lst if len(
        variant.cases) > 0 and len(variant.cases[0]) > 2)

    variant_flows = list()
    for variant in filtered_list:

        if len(variant.cases) == 0:
            continue
        
        case = variant.cases[0]
        number_of_activities = len(case)

        case_statistic = CaseStatistic()
        case_statistic.statistics = [ActivityStatistic() for i in range(number_of_activities)]

        for case in variant.cases:
            
            activity_list = list()            
            for x in range(0, len(case)):
                event = case[x]
                activity = case_statistic.statistics[x]
                activity.activity_name = event.activity

                activity_list.append(event.activity)
                
                time_before = get_time_before(case, x)
                time_taken = get_time_taken(case, x)
                time_after = get_time_after(case, x)

                lookup = [stat for stat in activity.resources if stat.resource == event.resource]

                stat = None

                if len(lookup) == 0:
                    stat = ResourceStatistic()
                    stat.resource = event.resource
                    activity.resources.append(stat)
                else:
                    stat = lookup[0]

                stat.add_to_resource(time_before, time_taken, time_after)

            case_statistic.activity_list = activity_list
                
        variant_flows.append(case_statistic)

    return variant_flows


def get_time_before(case, index):
    initial_event = case[0]
    current_event = case[index]
    difference = current_event.start_date - initial_event.start_date
    absolute = abs(difference.total_seconds())
    return absolute

def get_time_after(case, index):
    current_event = case[index]
    last_index = len(case) - 1
    end_event = case[last_index]
    difference = end_event.end_date - current_event.end_date
    absolute = abs(difference.total_seconds())
    return absolute


def get_time_taken(case, index):
    current_event = case[index]
    difference = current_event.end_date - current_event.start_date
    absolute = abs(difference.total_seconds())
    return absolute

class VariantFlows:
    def __init__(self):
        self.flows = []


class Flow:
    def __init__(self, activity_list, statistics):
        self.activity_list = activity_list
        self.statistics = statistics


class FlowStatistic:
    def __init__(self, resource, activity, time_before, time_taken, time_after):
        self.resource = resource
        self.activity = activity
        self.time_before = time_before
        self.time_taken = time_taken
        self.time_after = time_after

class CaseStatistic:
    def __init__(self):
      self.statistics = []
      self.activity_list = []
        

class ResourceStatistic:
    
    def __init__(self):
        self.resource = ""
        self.time_before = 0
        self.time_taken = 0
        self.time_after = 0
        self.occurrences = 0

    def add_to_resource(self, time_before, time_taken, time_after):
        self.time_before += time_before
        self.time_taken += time_taken
        self.time_after += time_after
        self.occurrences += 1


class ActivityStatistic:
    def __init__(self):
        self.activity_name = ""
        self.resources = []
