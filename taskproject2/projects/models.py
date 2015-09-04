from django.db import models

# Create your models here.
from core.models import Timestamped, UUidModel
from profiles.models import Profile


class Category(Timestamped, UUidModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        default_related_name = 'categories'
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Project(Timestamped, UUidModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        default_related_name = 'projects'
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __str__(self):
        return self.name


class Task(Timestamped, UUidModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        default_related_name = 'tasks'
        verbose_name = 'task'
        verbose_name_plural = 'tasks'

    def __str__(self):
        return self.name
