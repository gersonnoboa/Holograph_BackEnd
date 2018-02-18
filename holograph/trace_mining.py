import jsonpickle
import csv_handling
from datetime import datetime
import enums
import general_mining

def process_trace_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    mining = general_mining.get_variants(lst)
    info = mine_trace_info(mining)
    return jsonpickle.encode(info, unpicklable=False)


def mine_trace_info(lst):
    trace_variants = []

    for variant in lst:
        resources = set()
        for case in variant.cases:
            resources_in_case = set(event.resource for event in case)
            resources.update(resources_in_case)

        trace_variant = TraceVariant(variant.activity_list)
        variant.cases = sort_cases(variant.cases)
        general_stats = determine_stat_value(variant.cases)
        trace_variant.minimum_time = general_stats.minimum
        trace_variant.maximum_time = general_stats.maximum
        trace_variant.average_time = general_stats.average

        for resource in resources:
            cases_with_resource = []
            cases_without_resource = []

            for case in variant.cases:
                is_resource_present = determine_resource_existence(resource, case)
                cases_with_resource.append(case) if is_resource_present else cases_without_resource.append(case)
        
            resource = TraceResource(resource)

            resource.total_time_with = determine_total_time(cases_with_resource)
            resource.total_time_without = determine_total_time(cases_without_resource)

            stats_with = determine_stat_value(cases_with_resource)
            resource.minimum_time_with = stats_with.minimum
            resource.maximum_time_with = stats_with.maximum
            resource.average_time_with = stats_with.average

            stats_without = determine_stat_value(cases_without_resource)
            resource.minimum_time_without = stats_without.minimum
            resource.maximum_time_without = stats_without.maximum
            resource.average_time_without = stats_without.average

            update_facts(resource, trace_variant)
            trace_variant.resources.append(resource)
        
        trace_variants.append(trace_variant)
    
    return trace_variants


def update_facts(resource, trace_variant):
    quickest = trace_variant.get_fact(FactName.Quickest.value)
    revise_fact(quickest, resource.minimum_time_with, resource.name, False)

    slowest = trace_variant.get_fact(FactName.Slowest.value)
    revise_fact(slowest, resource.maximum_time_with, resource.name, True)

    above_average = trace_variant.get_fact(FactName.AboveAverage.value)
    accumulate_fact(above_average, resource.average_time_with, resource.name, True)

    below_average = trace_variant.get_fact(FactName.BelowAverage.value)
    accumulate_fact(below_average, resource.average_time_with, resource.name, False)

    positive_impact = trace_variant.get_fact(FactName.PositiveImpact.value)
    accumulate_fact_with_threshold(positive_impact, resource.average_time_with, resource.name, True, trace_variant.average_time)

    negative_impact = trace_variant.get_fact(FactName.NegativeImpact.value)
    accumulate_fact_with_threshold(
        negative_impact, resource.average_time_with, resource.name, False, trace_variant.average_time)

    most_involved = trace_variant.get_fact(FactName.MostInvolved.value)
    revise_fact(most_involved, resource.total_time_with, resource.name, True)

    least_involved = trace_variant.get_fact(FactName.LeastInvolved.value)
    revise_fact(least_involved, resource.total_time_with, resource.name, False)


def revise_fact(fact, new_value, resource_name, higher_is_better):
    revise_fact_with_threshold(fact, new_value, resource_name, higher_is_better, fact.value)


def revise_fact_with_threshold(fact, new_value, resource_name, higher_is_better, threshold):
    diff_condition = False
    equal_condition = False
    if (fact.value is None):
        diff_condition = True
    else:
        diff_condition = new_value > threshold if higher_is_better else new_value < threshold
        equal_condition = new_value == threshold
    
    if diff_condition:
        fact.value = new_value
        fact.elements.clear()
        fact.elements.append(resource_name)
    elif equal_condition:
        fact.elements.append(resource_name)


def accumulate_fact(fact, new_value, resource_name, higher_is_better):
    accumulate_fact_with_threshold(fact, new_value, resource_name, higher_is_better, fact.value)


def accumulate_fact_with_threshold(fact, new_value, resource_name, higher_is_better, threshold):
    diff_condition = False

    if (fact.value is None):
        fact.value = new_value
        diff_condition = True
    else:
        diff_condition = new_value >= threshold if higher_is_better else new_value < threshold

    if diff_condition:
        fact.elements.append(resource_name)


def update_element(element_list, name, should_clear):
    if should_clear:
        element_list.clear()
    
    element_list.append(name)


def determine_resource_existence(resource, case):
    is_resource_present = False
    for event in case:
        if event.resource == resource:
            is_resource_present = True
            break
    return is_resource_present


def sort_cases(cases):
    for case in cases:
        case.sort(key=lambda x: x.start_date, reverse=False)
    return cases


def determine_total_time(cases):
    if len(cases) < 1:
        return 0

    first_event = get_first_event_in_cases(cases)
    start_date = first_event.start_date
    last_event = get_last_event_in_cases(cases)
    end_date = last_event.end_date

    difference = end_date - start_date
    absolute = abs(difference.total_seconds())
    return absolute

def determine_stat_value(cases):
    if len(cases) < 1:
        return Stats(0,0,0)

    all_timedeltas = set()
    for case in cases:
        start_date = case[0].start_date
        end_date = get_last_event_in_case(case).end_date
        difference = end_date - start_date
        absolute = abs(difference.total_seconds())
        all_timedeltas.add(absolute)

    minimum = min(all_timedeltas)
    maximum = max(all_timedeltas)
    average = sum(all_timedeltas) / len(all_timedeltas)
    stats = Stats(minimum, maximum, average)
    return stats


def get_first_event_in_cases(cases):
    return cases[0][0]


def get_last_event_in_case(case):
    last_event_index = len(case) - 1
    last_event = case[last_event_index]
    return last_event
    

def get_last_event_in_cases(cases):
    last_case_index = len(cases) - 1
    last_case = cases[last_case_index]
    last_event = get_last_event_in_case(last_case)
    return last_event


class TraceVariant():
    total_time = 0
    average_time = 0
    minimum_time = 0
    maximum_time = 0
    facts = []

    def __init__(self, activity_list):
        self.activity_list = activity_list
        self.resources = []
        self.facts = []

    def get_fact(self, fact_name):
        all_facts = list(fact for fact in self.facts if fact.name == fact_name)
        if len(all_facts) == 0:
            fact = Fact(fact_name)
            self.facts.append(fact)
            return fact
        else:
            return all_facts[0]


class TraceResource():
    total_time_with = 0
    total_time_without = 0
    average_time_with = 0
    average_time_without = 0
    minimum_time_with = 0
    minimum_time_without = 0
    maximum_time_with = 0
    maximum_time_without = 0
    
    def __init__(self, name):
        self.name = name


class Stats():
    def __init__(self, minimum, maximum, average):
        self.minimum = minimum
        self.maximum = maximum
        self.average = average


class Fact():
    def __init__(self, name):
        self.name = name
        self.value = None
        self.elements = []


class FactName(enums.Enum):
    Quickest = "Quickest"
    Slowest = "Slowest"
    AboveAverage = "Above Average"
    BelowAverage = "Below Average"
    PositiveImpact = "Positive Impact"
    NegativeImpact = "Negative Impact"
    MostInvolved = "Most Involved"
    LeastInvolved = "Least Involved"
