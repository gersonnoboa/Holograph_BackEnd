import jsonpickle
import csv_handling
from datetime import datetime
import enums

def process_active_time_info(json_from_request, filepath):
    resource = str(json_from_request["resource"])
    activity = str(json_from_request["activity"])
    log_type = str(json_from_request["type"])
    parameter_one = str(json_from_request["parameterOne"])
    parameter_two = str(json_from_request["parameterTwo"])

    idx_resource = 0
    idx_activity = 0
    idx_parameter_one = 0
    idx_parameter_two = 0

    list = []

    with open(filepath, 'r') as f:
        for idx, line in enumerate(f):
            line = line.strip()

            if len(line) == 0:
                continue

            split = csv_handling.split_csv_line(line)

            if idx == 0:
                idx_resource = split.index(resource)
                idx_activity = split.index(activity)
                idx_parameter_one = split.index(parameter_one)
                if (log_type == enums.LogType.StartAndEndDate.value):
                    idx_parameter_two = split.index(parameter_two)
            else:
                res = split[idx_resource]
                act = split[idx_activity]
                if (log_type == enums.LogType.StartAndEndDate.value):
                    start_date = datetime.strptime(
                        split[idx_parameter_one], '%d-%m-%Y:%H.%M')
                    end_date = datetime.strptime(
                        split[idx_parameter_two], '%d-%m-%Y:%H.%M')
                    event = ActiveTimeEvent(res, act, start_date, end_date)
                    list.append(event)

    mining = mine_active_time_info(list)
    return jsonpickle.encode(mining, unpicklable=False)


def mine_active_time_info(list):
    activities = {event.activity for event in list}

    list_activities = []
    for activity in activities:
        all_events_for_activity = [
            event for event in list if event.activity == activity]
        resources = {event.resource for event in all_events_for_activity}
        list_resources = []
        for resource in resources:
            all_events_for_resource = [
                event for event in all_events_for_activity if event.resource == resource]
            total_active_time = sum([e.subtract_dates()
                                     for e in all_events_for_resource])
            event_count = len(all_events_for_resource)
            average_active_time = float(total_active_time) / float(event_count)
            list_resources.append(ActivityResource(
                resource, total_active_time, event_count, average_active_time))

        list_activities.append(Activity(activity, list_resources))

    return list_activities


class Activity:
    def __init__(self, activity, resources):
        self.activity = activity
        self.resources = resources


class ActivityResource:
    def __init__(self, resource, active_time, event_count, average_active_time):
        self.resource = resource
        self.active_time = active_time
        self.event_count = event_count
        self.average_active_time = average_active_time


class ActiveTimeEvent:
    def __init__(self, resource, activity, start_date, end_date):
        self.resource = resource
        self.activity = activity
        self.start_date = start_date
        self.end_date = end_date

    def subtract_dates(self):
        return (self.end_date - self.start_date).seconds
