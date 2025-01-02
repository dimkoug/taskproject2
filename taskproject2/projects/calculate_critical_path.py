# def calculate_cpm(data):
#     # Create a dictionary to map each activity to its predecessors
#     predecessors = {}
#     for activity in data:
#         predecessors[activity['activity']] = activity['predecessors']

#     critical_path = []
#     for activity in data:
#         es = 0
#         predecessors_list = predecessors[activity['activity']]
#         if predecessors_list:
#             ef_list = [d['ef'] for d in data if d['activity'] in predecessors_list]
#             es = max(ef_list)
#         activity['es'] = es
#         activity['ef'] = es + activity['duration']

#     # Create a dictionary to group the items that have the same predecessor
#     predecessors_dict = {}
#     for ditem in data:
#         for predecessor in ditem['predecessors']:
#             predecessors_dict.setdefault(predecessor, []).append(ditem)

#     for index, dactivity in enumerate(reversed(data)):
#         if index == 0:
#             dactivity['lf'] = dactivity['ef']
#         else:
#             items = predecessors_dict[dactivity['activity']]
#             durations = [ditem['ls'] for ditem in items]
#             dactivity['lf'] = min(durations)
#         dactivity['ls'] = dactivity['lf'] - dactivity['duration']
#         dactivity['slack'] = dactivity['lf'] - dactivity['ef']

#     for item in data:
#         if item['slack'] == 0:
#             critical_path.append(item['activity'])
#     print(critical_path)
#     return data
def calculate_cpm(data):
    """
    Calculate the Critical Path Method (CPM) for a given project dataset.

    Parameters:
    data (list of dict): Each dictionary contains the following keys:
        - 'activity': Activity name (str)
        - 'predecessors': List of predecessor activity names (list of str)
        - 'duration': Duration of the activity (int)

    Returns:
    list of dict: The input data with updated CPM fields ('es', 'ef', 'ls', 'lf', 'slack').
    """
    # Create a dictionary to map each activity to its predecessors
    predecessors = {activity['activity']: activity['predecessors'] for activity in data}
    
    # Step 1: Forward Pass (Calculate ES and EF)
    for activity in data:
        es = 0
        for pred in predecessors[activity['activity']]:
            pred_ef = next(d['ef'] for d in data if d['activity'] == pred)
            es = max(es, pred_ef)
        activity['es'] = es
        activity['ef'] = es + activity['duration']
    
    # Step 2: Build Predecessors Dictionary for Backward Pass
    successors = {activity['activity']: [] for activity in data}
    for activity in data:
        for pred in activity['predecessors']:
            successors[pred].append(activity['activity'])
    
    # Step 3: Backward Pass (Calculate LF, LS, and Slack)
    for activity in reversed(data):
        if not successors[activity['activity']]:  # If no successors
            activity['lf'] = activity['ef']
        else:
            successor_ls = [
                next(d['ls'] for d in data if d['activity'] == succ) for succ in successors[activity['activity']]
            ]
            activity['lf'] = min(successor_ls)
        activity['ls'] = activity['lf'] - activity['duration']
        activity['slack'] = activity['lf'] - activity['ef']
    
    # Step 4: Identify the Critical Path
    critical_path = [activity['activity'] for activity in data if activity['slack'] == 0]
    print(f"Critical Path: {critical_path}")
    
    return data