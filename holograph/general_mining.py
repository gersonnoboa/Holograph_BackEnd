import csv_handling
from datetime import datetime
import enums
import jsonpickle
import arrow
import string

def get_active_time_array(args_from_request, filepath):
    case_id = args_from_request.get("caseID")
    resource = args_from_request.get("resource")
    activity = args_from_request.get("activity")
    log_type = args_from_request.get("type")
    parameter_one = args_from_request.get("parameterOne")
    parameter_two = args_from_request.get("parameterTwo")

    idx_resource = 0
    idx_activity = 0
    idx_parameter_one = 0
    idx_parameter_two = 0

    lst = []

    with open(filepath, 'r') as f:

        format_string = ""
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

                format_string = infer_date_format_string(split)
            else:
                case = split[idx_case_id]
                res = split[idx_resource]
                act = split[idx_activity]
                date_one = split[idx_parameter_one]
                start_date = arrow.now()

                try:
                    start_date = arrow.get(date_one)
                except:
                    if format_string is not None:
                        start_date = arrow.get(date_one, format_string)

                if (log_type == enums.LogType.StartAndEndDate.value):

                    date_two = split[idx_parameter_two]
                    end_date = arrow.now()

                    try:
                        end_date = arrow.get(date_two)
                    except:
                        if format_string is not None:
                            end_date = arrow.get(date_two, format_string)

                    event = LogEvent(case, res, act, start_date, end_date)
                    lst.append(event)

    lst.sort(key=lambda x: x.start_date, reverse=False)
    return lst


def infer_date_format_string(split):
    format_string = ""
    for element in split:
        lower_element = element.lower()
        if "yyyy" in lower_element:
            format_string = element
            break

    fixed_string = format_string.replace("dd", "DD").replace("yyyy", "YYYY")
    return fixed_string

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
