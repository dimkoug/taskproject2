import os
from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMessage
from projects.models import *
from projects.calculate_critical_path import *

def generate_cpm_report(request,project_id):


    project = Project.objects.prefetch_related('category__company__profiles').get(category__company__profiles=request.user.profile.pk,id=project_id)
    title = 'Cpm report'
    tasks = Task.objects.prefetch_related('project__category__company__profiles','successor_tasks').filter(project__category__company__profiles=request.user.profile.pk,project_id=project.pk)
    cpmreport = CPMReport.objects.create(
        name=title,
        project=project
    )
    data = []
    for task in tasks:
        activity = {}
        activity['activity'] = task.name
        activity['early_start'] = activity['es'] = task.early_start
        activity['late_start'] = activity['ls'] = task.late_start
        activity['early_finish'] = activity['ef'] = task.early_finish
        activity['duration'] = task.duration
        activity['predecessors'] = []
        for pr in task.successor_tasks.all():
            activity['predecessors'].append(pr.from_task.name)
        data.append(activity)
    
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
    os.makedirs(temp_dir, exist_ok=True)
    
    graph_path = os.path.join(temp_dir, f"cpm_graph_{cpmreport.id}.png")
    gantt_path = os.path.join(temp_dir, f"gantt_chart_{cpmreport.id}.png")
    critical_path_file = os.path.join(temp_dir, f"critical_path.png")
    #paginated_path_file = os.path.join(temp_dir, f"paginated_gantt.png")
    full_report = os.path.join(temp_dir, f"full_gantt_report.pdf")
    
    
    
    critical_path = calculate_cpm(data)
    for item in critical_path:
        print(item)
        CPMReportData.objects.create(
            cpmreport=cpmreport,
            task=Task.objects.get(name=item['activity']),
            slack=item['slack'],
            es = item['es'],
            ef = item['ef'],
            ls = item['ls'],
            lf = item['lf']
        )
    critical_path_data = []
    
    for item in CPMReportData.objects.filter(cpmreport_id=cpmreport.id,slack=0):
        critical_path_data.append(item)
    
    critical_path = [activity['activity'] for activity in data if activity['slack'] == 0]
    print(critical_path)
    gantt_folder = os.path.join(settings.MEDIA_ROOT, 'gantt_pages', f'project_{project.id}')
    os.makedirs(gantt_folder, exist_ok=True)
    draw_activity_graph(data,critical_path, save_path=graph_path)
    draw_gantt_chart(data, critical_path,save_path=gantt_path)
    draw_critical_path_graph(data, critical_path, save_path=critical_path_file)
    # Save paginated gantt charts
    draw_paginated_gantt_chart(data,save_folder=gantt_folder, page_size=100)
    merge_gantt_images_to_pdf(temp_dir, full_report)


    with open(graph_path, 'rb') as graph_file:
        cpmreport.cpm_graph.save(os.path.basename(graph_path), File(graph_file))

    with open(gantt_path, 'rb') as gantt_file:
        cpmreport.gantt_chart.save(os.path.basename(gantt_path), File(gantt_file))

    cpmreport.save()
    return data



def send_report_email(request,report_id,emails):
    report = Report.objects.get(id=report_id)
    subject = 'Here is your PDF'
    body = 'Please find the attached PDF.'
    from_email = 'your_email@example.com'
    to_email = [request.user.email]

    # Load your PDF file
    file = report.report
    file.open('rb')  # ensure it's open
    pdf_data = file.read()
    file.close()
    filename = report.__str__()
    for email in emails:

        # Create the email
        email_msg = EmailMessage(
            subject,
            body,
            from_email,
            email,
        )

        # Attach the PDF file
        email_msg.attach(filename, pdf_data, 'application/pdf')

        # Send the email
        email_msg.send()


