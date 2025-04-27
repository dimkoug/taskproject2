import json
import datetime
import os
from PIL import Image
from django.utils import timezone
import matplotlib
matplotlib.use('Agg')  # <- This line fixes the Tkinter / RuntimeError
import matplotlib.pyplot as plt
import networkx as nx
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


def draw_critical_path_graph(data, critical_path, save_path=None):
    """
    Draws a simplified activity graph showing only the Critical Path.
    Much cleaner for large projects.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import networkx as nx
    import matplotlib.patches as mpatches

    G = nx.DiGraph()
    label_mapping = {}

    # Only critical activities
    critical_set = set(critical_path)

    for activity in data:
        if activity['activity'] not in critical_set:
            continue  # Skip non-critical activities
        node_label = f"{activity['activity']} ({activity['duration']}d)"
        G.add_node(activity['activity'])
        label_mapping[activity['activity']] = node_label
        for pred in activity['predecessors']:
            if pred in critical_set:
                G.add_edge(pred, activity['activity'])

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=False, node_size=1500, font_size=10, arrowsize=20, edge_color='red', width=2)
    nx.draw_networkx_labels(G, pos, labels=label_mapping, font_size=9)

    red_patch = mpatches.Patch(color='red', label='Critical Path Only')
    plt.legend(handles=[red_patch], loc='upper left')

    plt.title("Critical Path Graph (Simplified)", fontsize=14)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    else:
        plt.show()

    plt.close()




def draw_activity_graph(data, critical_path, save_path=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import networkx as nx
    import matplotlib.patches as mpatches

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

    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
    else:
        plt.show()

    plt.close()

def draw_gantt_chart(data,critical_path, save_path=None):
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
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def draw_paginated_gantt_chart(data, save_folder, page_size=100):
    from django.conf import settings
    import os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    total_tasks = len(data)
    pages = (total_tasks + page_size - 1) // page_size

    for page in range(pages):
        start_index = page * page_size
        end_index = min(start_index + page_size, total_tasks)
        page_tasks = data[start_index:end_index]

        fig, ax = plt.subplots(figsize=(12, 8))
        yticks = []
        ylabels = []
        for i, activity in enumerate(page_tasks):
            start = activity['es']
            duration = activity['duration']
            color = 'red' if activity['slack'] == 0 else 'blue'
            ax.barh(i, duration, left=start, height=0.4, align='center', color=color)
            yticks.append(i)
            ylabels.append(activity['activity'])

        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels)
        ax.set_xlabel("Time")
        ax.set_title(f"Gantt Chart (Page {page + 1})")
        red_patch = mpatches.Patch(color='red', label='Critical Path')
        blue_patch = mpatches.Patch(color='blue', label='Non-Critical Activities')
        plt.legend(handles=[red_patch, blue_patch])
        plt.grid(True, axis='x')
        plt.tight_layout()

        page_file = os.path.join(save_folder, f"gantt_page_{page + 1}.png")
        plt.savefig(page_file, bbox_inches='tight')
        plt.close()


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


def merge_gantt_images_to_pdf(image_folder, output_pdf_path):
    """
    Merges all PNG images in a folder into a single PDF file.
    """
    from PIL import Image
    import os

    images = []

    for file_name in sorted(os.listdir(image_folder)):
        if file_name.endswith(".png"):
            img_path = os.path.join(image_folder, file_name)
            try:
                with Image.open(img_path) as img:
                    img_rgb = img.convert('RGB').copy()  # Fully load and copy the image
                    images.append(img_rgb)
            except:
                pass
    if images:
        first_image = images[0]
        rest_images = images[1:]
        first_image.save(output_pdf_path, save_all=True, append_images=rest_images)
    else:
        raise ValueError("No images found in the folder!")


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

#
#calculate_cpm(data, draw_graph=True, draw_gantt=True)
#critical_path = calculate_cpm(data, draw_graph=False)

#print(json.dumps(critical_path, indent=4, sort_keys=True))


