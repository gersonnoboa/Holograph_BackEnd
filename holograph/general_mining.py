import csv_handling
from datetime import datetime
import enums
import jsonpickle

def get_active_time_array(json_from_request, filepath):
    case_id = str(json_from_request["caseID"])
    resource = str(json_from_request["resource"])
    activity = str(json_from_request["activity"])
    log_type = str(json_from_request["type"])
    parameter_one = str(json_from_request["parameterOne"])
    parameter_two = str(json_from_request["parameterTwo"])

    idx_resource = 0
    idx_activity = 0
    idx_parameter_one = 0
    idx_parameter_two = 0

    lst = []

    with open(filepath, 'r') as f:
        for idx, line in enumerate(f):
            line = line.strip()

            if len(line) == 0:
                continue

            split = csv_handling.split_csv_line(line)

            if idx == 0:
                idx_case_id = split.index(case_id)
                idx_resource = split.index(resource)
                idx_activity = split.index(activity)
                idx_parameter_one = split.index(parameter_one)
                if (log_type == enums.LogType.StartAndEndDate.value):
                    idx_parameter_two = split.index(parameter_two)
            else:
                case = split[idx_case_id]
                res = split[idx_resource]
                act = split[idx_activity]
                if (log_type == enums.LogType.StartAndEndDate.value):
                    start_date = datetime.strptime(
                        split[idx_parameter_one], '%d-%m-%Y:%H.%M')
                    end_date = datetime.strptime(
                        split[idx_parameter_two], '%d-%m-%Y:%H.%M')
                    event = LogEvent(case, res, act, start_date, end_date)
                    lst.append(event)

    lst.sort(key=lambda x: x.start_date, reverse=False)
    return lst


def get_variants(events):
    cases = get_grouped_cases(events)

    variants = []
    for case in cases:
        determine_variant(case, variants)

    return jsonpickle.encode(variants, unpicklable=False)


def determine_variant(case, variant_list):
    activities_in_case = list(event.activity for event in case)
    search_variant = list(variant for variant in variant_list if variant.activity_list == activities_in_case)
    if len(search_variant) != 0:
        search_variant[0].cases.append(case)
    else:
        variant = Variant(activities_in_case, [])
        variant.cases.append(case)
        variant_list.append(variant)


def get_grouped_cases(events):
    cases = {event.case_id for event in events}

    grouped_cases = []
    for case in cases:
        filtered_case = [event for event in events if event.case_id == case]
        grouped_cases.append(filtered_case)

    return grouped_cases


class Variant:
    def __init__(self, activity_list, cases):
        self.activity_list = activity_list
        self.cases = cases


class LogEvent:
    def __init__(self, case_id, resource, activity, start_date, end_date):
        self.case_id = case_id
        self.resource = resource
        self.activity = activity
        self.start_date = start_date
        self.end_date = end_date

    def subtract_dates(self):
        return (self.end_date - self.start_date).seconds
