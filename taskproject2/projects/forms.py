from django import forms

from core.forms import BootstrapForm


from .models import Category, Project, Task


class CategoryForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)


class ProjectForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Project
        fields = ('category', 'name',)


class TaskForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Task
        fields = ('project', 'name',)
