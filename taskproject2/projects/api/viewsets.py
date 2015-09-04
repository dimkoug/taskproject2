from rest_framework import authentication, permissions, viewsets, filters
from django_filters import rest_framework as django_filters


from ..models import Category, Project, Task
from .serializers import CategorySerializer, ProjectSerializer, TaskSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and creating categories."""

    queryset = Category.objects.order_by('title')
    serializer_class = CategorySerializer
    search_fields = ('title', )
    ordering_fields = ('title', )


class ProjectViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and creating projects."""

    queryset = Project.objects.order_by('title')
    serializer_class = ProjectSerializer
    search_fields = ('category', 'title', )
    ordering_fields = ('title', )


class TaskViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and creating tasks."""

    queryset = Task.objects.order_by('title')
    serializer_class = TaskSerializer
    search_fields = ('project', 'title', )
    ordering_fields = ('title', )
