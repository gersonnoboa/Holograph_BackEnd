import general_mining
import jsonpickle

def process_group_info(args_from_request, filepath):
    lst = general_mining.get_active_time_array(args_from_request, filepath)
    info = mine_group_info(lst)
    return jsonpickle.encode(info, unpicklable=False)

def mine_group_info(lst):
    return []