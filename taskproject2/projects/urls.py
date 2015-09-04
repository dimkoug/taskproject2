from django.urls import path

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
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name="project-list"),
    path('detail/<str:uuid>', ProjectDetailView.as_view(), name="project-detail"),
    path('create', ProjectCreateView.as_view(), name="project-create"),
    path('update/<uuid:uuid>', ProjectUpdateView.as_view(), name="project-update"),
    path('delete/<uuid:uuid>', ProjectDeleteView.as_view(), name="project-delete"),

    path('categories', CategoryListView.as_view(), name="category-list"),
    path('categories/detail/<uuid:uuid>', CategoryDetailView.as_view(), name="category-detail"),
    path('categories/create', CategoryCreateView.as_view(), name="category-create"),
    path('categories/update/<uuid:uuid>', CategoryUpdateView.as_view(), name="category-update"),
    path('categories/delete/<uuid:uuid>', CategoryDeleteView.as_view(), name="category-delete"),

    path('tasks', TaskListView.as_view(), name="task-list"),
    path('tasks/detail/<uuid:uuid>', TaskDetailView.as_view(), name="task-detail"),
    path('tasks/create', TaskCreateView.as_view(), name="task-create"),
    path('tasks/update/<uuid:uuid>', TaskUpdateView.as_view(), name="task-update"),
    path('tasks/delete/<uuid:uuid>', TaskDeleteView.as_view(), name="task-delete"),

]
