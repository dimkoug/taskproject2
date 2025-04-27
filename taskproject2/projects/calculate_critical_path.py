import json
import datetime
from django.utils import timezone
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
data = [
    {
        'activity': 'a',
        "duration": 3,
        "predecessors": []
    },
    {
        'activity': 'b',
        "duration": 4,
        "predecessors": ['a']
    },
    {
        'activity': 'c',
        "duration": 2,
        "predecessors": ['a']
    },
    {
        'activity': 'd',
        "duration": 5,
        "predecessors": ['b']
    },
    {
        'activity': 'e',
        "duration": 1,
        "predecessors": ['c']
    },
    {
        'activity': 'f',
        "duration": 2,
        "predecessors": ['c']
    },
    {
        'activity': 'g',
        "duration": 4,
        "predecessors": ['d', 'e']
    },
    {
        'activity': 'h',
        "duration": 3,
        "predecessors": ['f', 'g']
    }
]


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
    activity_lookup = {activity['activity']: activity for activity in data}
    
    project_start = data[0]['es']

    # Forward Pass
    for activity in data:
        if not activity['predecessors']:
            es = project_start
        else:
            pred_efs = [activity_lookup[pred]['ef'] for pred in activity['predecessors']]
            es = max(pred_efs)
        
        activity['es'] = es
        activity['ef'] = es + datetime.timedelta(days=activity['duration'])

    # Build successors
    successors = {activity['activity']: [] for activity in data}
    for activity in data:
        for pred in activity['predecessors']:
            successors[pred].append(activity['activity'])

    # Backward Pass
    project_finish = max(activity['ef'] for activity in data)

    for activity in reversed(data):
        if not successors[activity['activity']]:
            lf = project_finish
        else:
            succ_ls = [activity_lookup[succ]['ls'] for succ in successors[activity['activity']]]
            lf = min(succ_ls)

        activity['lf'] = lf
        activity['ls'] = lf - datetime.timedelta(days=activity['duration'])

        slack = (activity['ls'] - activity['es']).days
        activity['slack'] = max(slack, 0)

    # Critical Path
    critical_path = [activity['activity'] for activity in data if activity['slack'] == 0]
    print(f"Critical Path: {critical_path}")

    return data


# def calculate_cpm(data, draw_graph=False, draw_gantt=False):
#     """
#     Calculates the Critical Path Method (CPM) for a project using datetime.

#     Parameters:
#     ----------
#     data : list of dict
#         Each dict must have:
#             - 'activity' (str): Unique activity name.
#             - 'predecessors' (list of str): Names of predecessor activities.
#             - 'duration' (int or float): Duration in days.

#     Returns:
#     -------
#     list of dict
#         Each activity enriched with:
#             - 'es' (Early Start)
#             - 'ef' (Early Finish)
#             - 'ls' (Late Start)
#             - 'lf' (Late Finish)
#             - 'slack' (days)
#     """

#     # Assume no cycle check for now unless you implement detect_cycle()

#     # Quick lookup
#     activity_lookup = {activity['activity']: activity for activity in data}
    
#     # Step 1: Forward Pass
#     project_start = datetime.datetime.now()

#     for activity in data:
#         if not activity['predecessors']:
#             es = project_start
#         else:
#             pred_efs = [activity_lookup[pred]['ef'] for pred in activity['predecessors']]
#             es = max(pred_efs)
        
#         activity['es'] = es
#         activity['ef'] = es + datetime.timedelta(days=activity['duration'])

#     # Step 2: Build successors
#     successors = {activity['activity']: [] for activity in data}
#     for activity in data:
#         for pred in activity['predecessors']:
#             successors[pred].append(activity['activity'])

#     # Step 3: Backward Pass
#     # Find the project finish date
#     project_finish = max(activity['ef'].replace(tzinfo=None) for activity in data)

#     for activity in reversed(data):
#         if not successors[activity['activity']]:
#             lf = project_finish
#         else:
#             succ_ls = [activity_lookup[succ]['ls'] for succ in successors[activity['activity']]]
#             lf = min(succ_ls)

#         activity['lf'] = lf
#         activity['ls'] = lf - datetime.timedelta(days=activity['duration'])

#         slack = (activity['ls'].replace(tzinfo=None) - activity['es'].replace(tzinfo=None)).days
#         activity['slack'] = max(slack, 0)

#     # Step 4: Critical Path
#     critical_path = [activity['activity'] for activity in data if activity['slack'] == 0]
#     print(f"Critical Path: {critical_path}")

#     if draw_graph:
#         draw_activity_graph(data, critical_path)
#     if draw_gantt:
#         draw_gantt_chart(data)

#     return data

#calculate_cpm(data, draw_graph=True, draw_gantt=True)
#critical_path = calculate_cpm(data, draw_graph=False)

#print(json.dumps(critical_path, indent=4, sort_keys=True))


