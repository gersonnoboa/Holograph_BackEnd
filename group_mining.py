import general_mining
import jsonpickle

def general_processing(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_grouped_cases(lst)
    return mining


def process_group_activity_info(args_from_request, filepath):
    info = mine_group_activity_info(general_processing(args_from_request, filepath))
    return jsonpickle.encode(info, unpicklable=False)


def mine_group_activity_info(lst):
    filtered_list = list(case for case in lst if len(case) >= 2)

    case_connection = CaseConnection([])
    for case in filtered_list:
        limit = len(case) - 1
        for idx, event in enumerate(case):
            if idx == limit:
                continue
            next_event = case[idx + 1]
            case_connection.add_to_two_sided_connection(event, next_event)
    return case_connection


def process_group_resource_info(args_from_request, filepath):
    info = mine_group_resource_info(general_processing(args_from_request, filepath))
    return jsonpickle.encode(info, unpicklable=False)


def mine_group_resource_info(lst):
    filtered_list = list(case for case in lst if len(case) >= 2)

    resources = Resources()
    for case in filtered_list:
        limit = len(case) - 1
        for idx, event in enumerate(case):
            if idx == limit:
                continue
            next_event = case[idx + 1]
            resources.add_to_primary_resource(event, next_event)
    return resources

#By activities

class CaseConnection:
    def __init__(self, two_sided_connections):
        self.two_sided_connections = two_sided_connections

    def add_to_two_sided_connection(self, first_event, second_event):
        result = list(connection for connection in self.two_sided_connections if connection.from_resource == first_event.resource and connection.to_resource == second_event.resource and connection.from_activity == first_event.activity and connection.to_activity == second_event.activity)

        connection = None
        if len(result) == 0:
            connection = TwoSidedConnection(first_event, second_event)
            self.two_sided_connections.append(connection)
        else:
            connection = result[0]

        first_active_time = (first_event.end_date - first_event.start_date).seconds
        second_active_time = (second_event.end_date - second_event.start_date).seconds
        connection.total_time += first_active_time + second_active_time
        connection.occurrences += 1


class TwoSidedConnection:
    def __init__(self, first_event, second_event):
        self.from_activity = first_event.activity
        self.to_activity = second_event.activity
        self.from_resource = first_event.resource
        self.to_resource = second_event.resource
        self.total_time = 0
        self.occurrences = 0

# By resources

class Resources:
    def __init__(self):
        self.resources = list()

    def add_to_primary_resource(self, first_event, second_event):
        result = list(resource for resource in self.resources if resource.resource == first_event.resource)
        resource = None
        if len(result) == 0:
            resource = PrimaryResource(first_event.resource)
            self.resources.append(resource)
        else:
            resource = result[0]
        resource.add_to_secondary_resource(first_event, second_event)

class PrimaryResource:
    def __init__(self, resource):
        self.resource = resource
        self.secondary_resources = list()

    def add_to_secondary_resource(self, first_event, second_event):
        result = list(resource for resource in self.secondary_resources if resource.resource == second_event.resource)
        resource = None
        if len(result) == 0:
            resource = SecondaryResource(second_event.resource)
            self.secondary_resources.append(resource)
        else:
            resource = result[0]
        resource.add_to_activities(first_event, second_event)


class SecondaryResource:
    def __init__(self, resource):
        self.resource = resource
        self.activities = list()

    def add_to_activities(self, first_event, second_event):
        result = list(activity for activity in self.activities if activity.from_activity == first_event.activity and activity.to_activity == second_event.activity)
        activity = None
        if len(result) == 0:
            activity = ActivityConnection(first_event, second_event)
            self.activities.append(activity)
        else:
            activity = result[0]
        first_active_time = (first_event.end_date - first_event.start_date).seconds
        second_active_time = (second_event.end_date - second_event.start_date).seconds
        activity.total_time += first_active_time + second_active_time
        activity.occurrences += 1


class ActivityConnection:
    def __init__(self, first_event, second_event):
        self.from_activity = first_event.activity
        self.to_activity = second_event.activity
        self.total_time = 0
        self.occurrences = 0
