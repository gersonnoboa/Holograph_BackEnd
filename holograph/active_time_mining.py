import jsonpickle
import csv_handling
from datetime import datetime
import enums
import general_mining

def process_active_time_info(json_from_request, filepath):
    lst = general_mining.get_active_time_array(json_from_request, filepath)
    mining = mine_active_time_info(lst)
    return jsonpickle.encode(mining, unpicklable=False)


def mine_active_time_info(lst):
    activities = {event.activity for event in lst}

    list_activities = []
    for activity in activities:
        all_events_for_activity = [event for event in lst if event.activity == activity]
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
