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
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name="project-list"),
    path('detail/<int:pk>/', ProjectDetailView.as_view(), name="project-detail"),
    path('create/', ProjectCreateView.as_view(), name="project-create"),
    path('update/<int:pk>/', ProjectUpdateView.as_view(), name="project-update"),
    path('delete/<int:pk>/', ProjectDeleteView.as_view(), name="project-delete"),

    path('categories/', CategoryListView.as_view(), name="category-list"),
    path('categories/detail/<int:pk>/', CategoryDetailView.as_view(), name="category-detail"),
    path('categories/create', CategoryCreateView.as_view(), name="category-create"),
    path('categories/update/<int:pk>/', CategoryUpdateView.as_view(), name="category-update"),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name="category-delete"),

    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/detail/<int:pk>/', TaskDetailView.as_view(), name="task-detail"),
    path('tasks/create/', TaskCreateView.as_view(), name="task-create"),
    path('tasks/update/<int:pk>/', TaskUpdateView.as_view(), name="task-update"),
    path('tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name="task-delete"),


    path('cpm/reports/', CPMReportListView.as_view(), name="cpmreport-list"),
    path('cpm/reports/<int:pk>/', CPMReportDetailView.as_view(), name="cpmreport-detail"),


    path('get_sb_projects_data/', get_sb_projects_data, name='sb-projects'),
    path('get_sb_categories_data/', get_sb_categories_data, name='sb-categories'),
    path('get_tasks_for_sb/', get_tasks_for_sb, name='get_tasks_for_sb'),

]
