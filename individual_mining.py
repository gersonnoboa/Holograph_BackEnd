import general_mining
import jsonpickle
import flow_mining

def process_individual_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_variants(lst)
    flow_info = flow_mining.mine_flow_info(mining)
    info = mine_individual_info(flow_info)
    return jsonpickle.encode(info, unpicklable=False)


def mine_individual_info(lst):
    filtered_list = list(variant for variant in lst if len(variant.activity_list) >= 3)

    individual_info = list()

    for variant in filtered_list:
        activity_list_count = len(variant.activity_list)

        divs = Divisions(activity_list_count)

        initial = variant.statistics[:divs.initial_end]
        middle = variant.statistics[divs.middle_start:divs.middle_end]
        final = variant.statistics[divs.final_start:]

        division_results = DivisionResults(variant.activity_list, process_initial_information(
            initial), process_initial_information(middle), process_initial_information(final))
        individual_info.append(division_results)

    return individual_info


def process_initial_information(lst):
    info = list()
    for idx, element in enumerate(lst):
        element.resources.sort(key=lambda x: x.time_after)
        division_specific = DivisionSpecific(
            element.activity_name, 
            idx, 
            element.resources
        )
        info.append(division_specific)
    return info


class Divisions:
    def __init__(self, activities_number):
        self.initial_start = 0
        self.initial_end = int(activities_number / 3)

        self.final_end = activities_number
        self.final_start = activities_number - int(activities_number / 3)

        self.middle_start = self.initial_end
        self.middle_end = self.final_start


class DivisionResults:
    def __init__(self, activity_list, initial, middle, final):
        self.activity_list = activity_list
        self.initial = initial
        self.middle = middle
        self.final = final


class DivisionSpecific:
    def __init__(self, activity, order, resources):
        self.activity = activity
        self.order = order
        self.resources = resources
