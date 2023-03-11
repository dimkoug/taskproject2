def calculate_cpm(data):
    # Create a dictionary to map each activity to its predecessors
    predecessors = {}
    for activity in data:
        predecessors[activity['activity']] = activity['predecessors']

    critical_path = []
    for activity in data:
        es = 0
        predecessors_list = predecessors[activity['activity']]
        if predecessors_list:
            ef_list = [d['ef'] for d in data if d['activity'] in predecessors_list]
            es = max(ef_list)
        activity['es'] = es
        activity['ef'] = es + activity['duration']

    # Create a dictionary to group the items that have the same predecessor
    predecessors_dict = {}
    for ditem in data:
        for predecessor in ditem['predecessors']:
            predecessors_dict.setdefault(predecessor, []).append(ditem)

    for index, dactivity in enumerate(reversed(data)):
        if index == 0:
            dactivity['lf'] = dactivity['ef']
        else:
            items = predecessors_dict[dactivity['activity']]
            durations = [ditem['ls'] for ditem in items]
            dactivity['lf'] = min(durations)
        dactivity['ls'] = dactivity['lf'] - dactivity['duration']
        dactivity['slack'] = dactivity['lf'] - dactivity['ef']

    for item in data:
        if item['slack'] == 0:
            critical_path.append(item['activity'])
    print(critical_path)
    return data