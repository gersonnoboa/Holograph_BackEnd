import csv_handling
from datetime import datetime
from dateutil.parser import parse
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
    remote_date_format_string = args_from_request.get("dateTimeFormat")
    local_date_format_string = None
    idx_resource = 0
    idx_activity = 0
    idx_parameter_one = 0
    idx_parameter_two = 0

    lst = []

    with open(filepath, 'r') as f:
        reader = csv_handling.get_csv_reader(f)

        split = next(reader)

        idx_case_id = split.index(case_id)
        idx_resource = split.index(resource)
        idx_activity = split.index(activity)
        idx_parameter_one = split.index(parameter_one)
        if (log_type == enums.LogType.StartAndEndDate.value):
            idx_parameter_two = split.index(parameter_two)

        local_date_format_string = infer_date_format_string(split)

        for row in reader:
            case = row[idx_case_id]
            res = row[idx_resource]
            act = row[idx_activity]
            date_one = row[idx_parameter_one]
            start_date = try_date_time_retrieval(date_one, remote_date_format_string, local_date_format_string)

            event = LogEvent(case, res, act, start_date)

            if (log_type == enums.LogType.StartAndEndDate.value):
                date_two = row[idx_parameter_two]
                end_date = try_date_time_retrieval(date_two, remote_date_format_string, local_date_format_string)
                event.end_date = end_date

            lst.append(event)


    lst.sort(key=lambda x: x.start_date, reverse=False)
    return lst


def try_date_time_retrieval(string_date, priority_format_string, secondary_format_string):
    ret_date = None
    if priority_format_string is not None:
        try:
            ret_date = arrow.get(string_date, fix_date_format_string(priority_format_string))
        except:
            converted_format_string = convert_date_format_string_to_python(priority_format_string)
            ret_date = datetime.strptime(string_date, converted_format_string)
    else:
        try:
            ret_date = arrow.get(string_date)
        except:
            if secondary_format_string is not None:
                try:
                    ret_date = arrow.get(string_date, fix_date_format_string(secondary_format_string))
                except:
                    converted_format_string = convert_date_format_string_to_python(secondary_format_string)
                    ret_date = datetime.strptime(string_date, converted_format_string)


    return ret_date


def infer_date_format_string(split):
    format_string = ""
    for element in split:
        lower_element = element.lower()
        if "yyyy" in lower_element:
            format_string = element
            break

    fixed_string = fix_date_format_string(format_string)
    return fixed_string


def convert_date_format_string_to_python(str):
    return (str.replace("yyyy", "%Y")
           .replace("yy", "%y")
           .replace("dd", "%d")
           .replace("MM", "%m")
           .replace("HH", "%H")
           .replace("mm", "%M")
           .replace("SS", "%S"))

def fix_date_format_string(format_string):
    return format_string.replace("dd", "DD").replace("yyyy", "YYYY").replace("yy", "YY")


def get_variants(events):
    cases = get_grouped_cases(events)

    variants = []
    for case in cases:
        determine_variant(case, variants)

    variants.sort(key=lambda x: len(x.cases), reverse=True)
    return variants


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

    for cases in grouped_cases:
        cases.sort(key=lambda x: x.start_date)
        
    return grouped_cases


class Variant:
    def __init__(self, activity_list, cases):
        self.activity_list = activity_list
        self.cases = cases


class LogEvent:
    def __init__(self, case_id, resource, activity, start_date):
        self.case_id = case_id
        self.resource = resource
        self.activity = activity
        self.start_date = start_date
        self.end_date = arrow.now()

    def subtract_dates(self):
        return (self.end_date - self.start_date).seconds
