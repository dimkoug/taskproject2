from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import send_mail
from users.models import User
from projects.models import Project


@shared_task
def send_email(email, project):
    user = User.objects.get(email=email)
    project = Project.objects.get(pk=project)
    title = 'Create Project'
    msg_plain = render_to_string('form_email.txt', {
        'user': user.email, 'title': project.title,
        })
    msg_html = render_to_string('form_email.html', {
        'user': user.email, 'title': project.title,

    })
    send_mail(
        title,
        msg_plain,
        user.email,
        [user.email],
        html_message=msg_html,
    )
    return 'Project with title {}  created with success!'.format(project.title)
