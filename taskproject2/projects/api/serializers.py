from rest_framework import serializers
from rest_framework.reverse import reverse

from ..models import Category, Project, Task


class CategorySerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'profile', 'title', 'links')

    def get_links(self, obj):
        request = self.context['request']

        return {
            'self': reverse('category-detail',
                            kwargs={'pk': obj.pk}, request=request),
            'projects': reverse(
                'project-list', request=request) + '?category={}'.format(
                    obj.pk),
        }


class ProjectSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'profile', 'category',  'title', 'links')

    def get_links(self, obj):
        request = self.context['request']

        return {
            'self': reverse('project-detail',
                            kwargs={'pk': obj.pk}, request=request),
            'tasks': reverse(
                'task-list', request=request) + '?project={}'.format(
                    obj.pk),
        }


class TaskSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'profile', 'project',  'title', 'links')

    def get_links(self, obj):
        request = self.context['request']

        return {
            'self': reverse('task-detail',
                            kwargs={'pk': obj.pk}, request=request),
        }
