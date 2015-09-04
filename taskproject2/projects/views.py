from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


from core.mixins import ProtectedViewMixin, ModelMixin

from .models import Category, Project, Task
from .forms import CategoryForm, ProjectForm, TaskForm


class UUidMixinQuery:
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(uuid=pk)
        obj = queryset.get()
        return obj


class CategoryListView(ProtectedViewMixin, ModelMixin, ListView):

    model = Category
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        return self.model.objects.filter(profile=self.request.user.profile)


class CategoryDetailView(ProtectedViewMixin, ModelMixin,
                         UUidMixinQuery,  DetailView):

    model = Category
    pk_url_kwarg = 'uuid'


class CategoryCreateView(ProtectedViewMixin, ModelMixin, CreateView):
    model = Category
    form_class = CategoryForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.profile = self.request.user.profile
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:category-list')


class CategoryUpdateView(ProtectedViewMixin, ModelMixin,
                         UUidMixinQuery, UpdateView):
    model = Category
    form_class = CategoryForm
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)


    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:category-list')


class CategoryDeleteView(ProtectedViewMixin, ModelMixin,
                         UUidMixinQuery, DeleteView):
    model = Category
    success_url = reverse_lazy('projects:category-list')
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)


class ProjectListView(ProtectedViewMixin, ModelMixin, ListView):

    model = Project
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        return self.model.objects.select_related('category__profile').filter(
                category__profile_id=self.request.user.profile.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectDetailView(ProtectedViewMixin, ModelMixin,
                        UUidMixinQuery, DetailView):

    model = Project
    pk_url_kwarg = 'uuid'


class ProjectCreateView(ProtectedViewMixin, ModelMixin, CreateView):
    model = Project
    form_class = ProjectForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:project-list')


class ProjectUpdateView(ProtectedViewMixin, ModelMixin,
                        UUidMixinQuery, UpdateView):
    model = Project
    form_class = ProjectForm
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().category.profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:project-list')


class ProjectDeleteView(ProtectedViewMixin, ModelMixin,
                        UUidMixinQuery, DeleteView):
    model = Project
    success_url = reverse_lazy('projects:project-list')
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().category.profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)


class TaskListView(ProtectedViewMixin, ModelMixin, ListView):

    model = Task
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        return self.model.objects.select_related('project__category__profile').filter(
                project__category__profile_id=self.request.user.profile.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TaskDetailView(ProtectedViewMixin, ModelMixin, UUidMixinQuery, DetailView):

    model = Task
    pk_url_kwarg = 'uuid'


class TaskCreateView(ProtectedViewMixin, ModelMixin, CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:task-list')


class TaskUpdateView(ProtectedViewMixin, ModelMixin,
                     UUidMixinQuery, UpdateView):
    model = Task
    form_class = TaskForm
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().project.category.profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()
        if 'continue' in self.request.POST:
            app = obj._meta.app_label
            model = obj.__class__.__name__.lower()
            pk = {'uuid':obj.uuid}
            url = reverse_lazy('{}:{}-update'.format(app,model), kwargs=pk)
            return redirect(url)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('projects:task-list')


class TaskDeleteView(ProtectedViewMixin, ModelMixin,
                     UUidMixinQuery, DeleteView):
    model = Task
    success_url = reverse_lazy('projects:task-list')
    pk_url_kwarg = 'uuid'

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.pk != self.get_object().project.category.profile.pk:
            raise PermissionDenied()
        return super().dispatch(*args, **kwargs)
