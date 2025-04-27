from django.urls import path
from core.patterns import get_patterns
from .functions import (
    get_sb_projects_data,
    get_sb_categories_data,
    get_tasks_for_sb
)

from . import views


app_name = 'projects'

urlpatterns = get_patterns(app_name,'views') + [
    path('get_sb_projects_data/', get_sb_projects_data, name='sb-projects'),
    path('get_sb_categories_data/', get_sb_categories_data, name='sb-categories'),
    path('get_tasks_for_sb/', get_tasks_for_sb, name='get_tasks_for_sb'),
    
    path('add/predecessor/<int:task_id>/', views.add_predecessor, name='add-predecessor'),

    path('predecessor/delete/<int:task>/<int:id>/', views.delete_predecessor, name='predecessor_delete'),
    path('project/report/<int:project_id>/',views.download_full_project_report_pdf,name="project-report"),
    path('gantt-chart/<int:project_id>/', views.gantt_chart_view, name='gantt_chart'),

]
