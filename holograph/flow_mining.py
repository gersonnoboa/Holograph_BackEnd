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
    filtered_list = list(variant for variant in lst if len(variant.cases) > 0 and len(variant.cases[0]) > 2)

    variant_flows = list()
    for variant in filtered_list:
        statistics = list()
        for case in variant.cases:
            resources_in_case = set(event.resource for event in case)
            if len(resources_in_case) > 1:
                statistic_group = list()
                for x in range(0, len(case)):
                    event = case[x]
                    resource = event.resource
                    activity = event.activity
                    time_before = get_time_before(case, x)
                    time_taken = get_time_taken(case, x)
                    time_after = get_time_after(case, x)
                    flow_statistic = FlowStatistic(
                        resource, activity, time_before, time_taken, time_after)
                    statistic_group.append(flow_statistic)
                statistics.append(statistic_group)

        if len(statistics) > 0:
            flow = Flow(variant.activity_list, statistics)
            variant_flows.append(flow)
            if len(variant_flows) == 5:
                break

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
