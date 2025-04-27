import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
# data = [
#     {
#         'activity': 'a',
#         "duration": 3,
#         "predecessors": []
#     },
#     {
#         'activity': 'b',
#         "duration": 4,
#         "predecessors": ['a']
#     },
#     {
#         'activity': 'c',
#         "duration": 2,
#         "predecessors": ['a']
#     },
#     {
#         'activity': 'd',
#         "duration": 5,
#         "predecessors": ['b']
#     },
#     {
#         'activity': 'e',
#         "duration": 1,
#         "predecessors": ['c']
#     },
#     {
#         'activity': 'f',
#         "duration": 2,
#         "predecessors": ['c']
#     },
#     {
#         'activity': 'g',
#         "duration": 4,
#         "predecessors": ['d', 'e']
#     },
#     {
#         'activity': 'h',
#         "duration": 3,
#         "predecessors": ['f', 'g']
#     }
# ]


def detect_cycle(data):
    """
    Detects a cycle in the activities data.
    Raises an exception if a cycle is found.
    """
    activity_lookup = {activity['activity']: activity for activity in data}
    visited = set()
    visiting = set()

    def dfs(activity_name):
        if activity_name in visiting:
            raise ValueError(f"Cycle detected at activity: {activity_name}")
        if activity_name in visited:
            return
        visiting.add(activity_name)
        for neighbor in activity_lookup[activity_name]['predecessors']:
            dfs(neighbor)
        visiting.remove(activity_name)
        visited.add(activity_name)

    for activity in data:
        if activity['activity'] not in visited:
            dfs(activity['activity'])


def draw_activity_graph(data, critical_path):
    """
    Draws the activity dependency graph.
    Critical path edges are highlighted in red.
    Nodes show activity name and duration.
    """
    G = nx.DiGraph()
    label_mapping = {}
    for activity in data:
        node_label = f"{activity['activity']} ({activity['duration']}d)"
        G.add_node(activity['activity'])
        label_mapping[activity['activity']] = node_label
        for pred in activity['predecessors']:
            G.add_edge(pred, activity['activity'])

    pos = nx.spring_layout(G, seed=42)

    edge_colors = []
    for u, v in G.edges():
        if u in critical_path and v in critical_path:
            u_index = critical_path.index(u)
            if u_index + 1 < len(critical_path) and critical_path[u_index + 1] == v:
                edge_colors.append('red')
            else:
                edge_colors.append('gray')
        else:
            edge_colors.append('gray')

    nx.draw(G, pos, with_labels=False, node_size=1500, font_size=12, arrowsize=20, edge_color=edge_colors, width=2)
    nx.draw_networkx_labels(G, pos, labels=label_mapping, font_size=10)

    red_patch = mpatches.Patch(color='red', label='Critical Path')
    plt.legend(handles=[red_patch])
    plt.title("Project Activity Graph with Durations")
    plt.show()

def draw_gantt_chart(data):
    """
    Draws a Gantt chart based on Early Start (ES) and Duration.
    Critical path activities are highlighted in red.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    yticks = []
    ylabels = []
    for i, activity in enumerate(data):
        start = activity['es']
        duration = activity['duration']
        color = 'red' if activity['slack'] == 0 else 'blue'
        ax.barh(i, duration, left=start, height=0.4, align='center', color=color)
        yticks.append(i)
        ylabels.append(activity['activity'])

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Time")
    ax.set_title("Gantt Chart (CPM Scheduling)")
    red_patch = mpatches.Patch(color='red', label='Critical Path')
    blue_patch = mpatches.Patch(color='blue', label='Non-Critical Activities')
    plt.legend(handles=[red_patch, blue_patch])
    plt.grid(True, axis='x')
    plt.tight_layout()
    plt.show()


def calculate_cpm(data, draw_graph=False, draw_gantt=False):
    """
    Calculates the Critical Path Method (CPM) for a project.

    Parameters:
    ----------
    data : list of dict
        A list where each element is a dictionary with the following keys:
            - 'activity' (str): The unique name of the activity.
            - 'predecessors' (list of str): A list of activity names that must be completed before this activity starts.
            - 'duration' (int or float): The time required to complete the activity.

    draw_graph : bool, optional (default=False)
        If True, draws a visualization of the activity dependency graph.

    Returns:
    -------
    list of dict
        The input list with additional keys for each activity:
            - 'es' (Early Start)
            - 'ef' (Early Finish)
            - 'ls' (Late Start)
            - 'lf' (Late Finish)
            - 'slack' (Float time)
    
    Raises:
    ------
    ValueError
        If a circular dependency (cycle) is detected in the input data.
    """

    # Step 0: Detect cycles before proceeding
    detect_cycle(data)
    

    
    # Build quick lookup for activities
    activity_lookup = {activity['activity']: activity for activity in data}
    
    # Step 1: Forward Pass
    for activity in data:
        es = 0
        for pred in activity['predecessors']:
            pred_ef = activity_lookup[pred]['ef']
            es = max(es, pred_ef)
        activity['es'] = es
        activity['ef'] = es + activity['duration']
    
    # Step 2: Build successors
    successors = {activity['activity']: [] for activity in data}
    for activity in data:
        for pred in activity['predecessors']:
            successors[pred].append(activity['activity'])
    
    # Step 3: Backward Pass
    for activity in reversed(data):
        if not successors[activity['activity']]:
            activity['lf'] = activity['ef']
        else:
            successor_ls = [activity_lookup[succ]['ls'] for succ in successors[activity['activity']]]
            activity['lf'] = min(successor_ls)
        activity['ls'] = activity['lf'] - activity['duration']
        activity['slack'] = activity['lf'] - activity['ef']
    
    # Step 4: Critical Path
    critical_path = [activity['activity'] for activity in data if activity['slack'] == 0]
    print(f"Critical Path: {critical_path}")
    
    if draw_graph:
        draw_activity_graph(data, critical_path)
    if draw_gantt:
        draw_gantt_chart(data)
    
    return data

# calculate_cpm(data, draw_graph=True, draw_gantt=True)
# critical_path = calculate_cpm(data, draw_graph=False)

# print(json.dumps(critical_path, indent=4, sort_keys=True))


