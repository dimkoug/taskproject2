from rest_framework.routers import DefaultRouter

from . import viewsets


router = DefaultRouter(trailing_slash=False)
router.register('categories', viewsets.CategoryViewSet)
router.register('projects', viewsets.ProjectViewSet)
router.register('tasks', viewsets.TaskViewSet)
