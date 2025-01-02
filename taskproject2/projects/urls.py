from django.urls import path

from .functions import (
    get_sb_projects_data,
    get_sb_categories_data,
    get_tasks_for_sb
)


from .views import (
    CategoryListView,
    CategoryDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,

    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,

    TaskListView,
    TaskDetailView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,

    CPMReportListView,
    CPMReportDetailView,
    gantt_chart_view,
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name="project-list"),
    path('view/<int:pk>/', ProjectDetailView.as_view(), name="project-view"),
    path('add/', ProjectCreateView.as_view(), name="project-add"),
    path('change/<int:pk>/', ProjectUpdateView.as_view(), name="project-change"),
    path('delete/<int:pk>/', ProjectDeleteView.as_view(), name="project-delete"),

    path('categories/', CategoryListView.as_view(), name="category-list"),
    path('categories/view/<int:pk>/', CategoryDetailView.as_view(), name="category-view"),
    path('categories/add/', CategoryCreateView.as_view(), name="category-add"),
    path('categories/change/<int:pk>/', CategoryUpdateView.as_view(), name="category-change"),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name="category-delete"),

    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/view/<int:pk>/', TaskDetailView.as_view(), name="task-view"),
    path('tasks/add/', TaskCreateView.as_view(), name="task-add"),
    path('tasks/change/<int:pk>/', TaskUpdateView.as_view(), name="task-change"),
    path('tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name="task-delete"),


    path('cpm/reports/', CPMReportListView.as_view(), name="cpmreport-list"),
    path('cpm/reports/<int:pk>/', CPMReportDetailView.as_view(), name="cpmreport-detail"),


    path('get_sb_projects_data/', get_sb_projects_data, name='sb-projects'),
    path('get_sb_categories_data/', get_sb_categories_data, name='sb-categories'),
    path('get_tasks_for_sb/', get_tasks_for_sb, name='get_tasks_for_sb'),

    path('gantt-chart/<int:project_id>/', gantt_chart_view, name='gantt_chart'),

]
