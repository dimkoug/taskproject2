import datetime
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


from core.functions import is_ajax
from core.mixins import PaginationMixin, ModelMixin, SuccessUrlMixin,FormMixin,QueryListMixin, AjaxDeleteMixin

from .models import Category, Project, Task, Predecessor, CPMReport,CPMReportData
from .forms import CategoryForm, ProjectForm, TaskForm, PredecessorFormSet
from .calculate_critical_path import calculate_cpm


class BaseListView(PaginationMixin, ModelMixin, LoginRequiredMixin, ListView):
    def dispatch(self, *args, **kwargs):
        self.ajax_list_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if is_ajax(request):
            html_form = render_to_string(
                self.ajax_list_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)




class CategoryListView(BaseListView,QueryListMixin):
    model = Category
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset


class CategoryDetailView(LoginRequiredMixin,ModelMixin,DetailView):
    model = Category

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset



class CategoryCreateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, CreateView):
    model = Category
    form_class = CategoryForm

    def form_valid(self,form):
        form.instance.profile = self.request.user.profile
        form.save()
        return super().form_valid(form)


class CategoryUpdateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, UpdateView):
    model = Category
    form_class = CategoryForm


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset



class CategoryDeleteView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Category
    ajax_partial = 'partials/ajax_delete_modal.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile_id=self.request.user.profile.id)
        return queryset



class ProjectListView(BaseListView):

    model = Project
    paginate_by = 100  # if pagination is desired
    queryset = Project.objects.select_related('category__profile', 'parent')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                category__profile_id=self.request.user.profile.pk)
        category = self.request.GET.get('category')
        parent = self.request.GET.get('parent')
        if category:
            queryset = queryset.filter(category_id=category)
        if parent:
            queryset = queryset.filter(parent_id=parent)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectDetailView(LoginRequiredMixin,DetailView):
    model = Project
    queryset = Project.objects.select_related('category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                category__profile_id=self.request.user.profile.pk)
        return queryset


class ProjectCreateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, CreateView):
    model = Project
    form_class = ProjectForm




class ProjectUpdateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    queryset = Project.objects.select_related('category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                category__profile_id=self.request.user.profile.pk)
        return queryset


class ProjectDeleteView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Project
    ajax_partial = 'partials/ajax_delete_modal.html'
    queryset = Project.objects.select_related('category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                category__profile_id=self.request.user.profile.pk)
        return queryset


class TaskListView(BaseListView):
    model = Task
    paginate_by = 100  # if pagination is desired
    queryset = Task.objects.select_related('project__category__profile').prefetch_related('predecessors')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset

class TaskDetailView(LoginRequiredMixin,DetailView):
    model = Task
    queryset = Task.objects.select_related('project__category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset


class TaskCreateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, CreateView):
    model = Task
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formsets'] = [
            {
                'title': 'Predecessors',
                'formset': PredecessorFormSet(
                    self.request.POST or None,
                    queryset=Predecessor.objects.select_related(
                        'from_task', 'to_task')),
                "sb_url": reverse("projects:get_tasks_for_sb")
            },
        ]
        return context

    def form_valid(self, form):
        if form.is_valid():
            obj = form.save(commit=False)
            formsets = [
                PredecessorFormSet(self.request.POST, instance=obj),
            ]
            for formset in formsets:
                for f in formset:
                    for field in f.fields:
                        if 'category' == field:
                            print("category queryset")
                            f['category'].queryset = Category.objects.all()
                if formset.is_valid():
                    obj.save()
                    formset.save()
                else:
                    print(formset.non_form_errors())
                    print("formset errors:", formset.errors)
                    return super().form_invalid(form)
        return super().form_valid(form)


class TaskUpdateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, UpdateView):
    model = Task
    form_class = TaskForm
    queryset = Task.objects.select_related('project__category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formsets'] = [
            {
                'title': 'Predecessors',
                'formset': PredecessorFormSet(
                    self.request.POST or None,
                    instance=self.get_object(),
                    queryset=Predecessor.objects.select_related(
                        'from_task', 'to_task')),
                "sb_url": reverse("projects:get_tasks_for_sb")
            },
        ]
        return context

    def form_valid(self, form):
        if form.is_valid():
            obj = form.save(commit=False)
            formsets = [
                PredecessorFormSet(self.request.POST, instance=obj),
            ]
            for formset in formsets:
                for f in formset:
                    print(f.fields)
                    for field in f.fields:
                        if 'category' == field:
                            print("category queryset")
                            f['category'].queryset = Category.objects.all()
                if formset.is_valid():
                    obj.save()
                    formset.save()
                else:
                    print(formset.non_form_errors())
                    print("formset errors:", formset.errors)
                    return super().form_invalid(form)
        return super().form_valid(form)


class TaskDeleteView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Task
    success_url = reverse_lazy('projects:task-list')
    ajax_partial = 'partials/ajax_delete_modal.html'
    queryset = Task.objects.select_related('project__category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset


class CPMReportListView(PaginationMixin, ModelMixin, LoginRequiredMixin, ListView):
    model = CPMReport
    paginate_by = 10  # if pagination is desired
    queryset = CPMReport.objects.select_related('project__category__profile')

    def dispatch(self, *args, **kwargs):
        self.ajax_list_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        project_id = request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.select_related('category__profile').get(category__profile_id=self.request.user.profile.pk,id=project_id)
                title = 'Cpm report'
                tasks = Task.objects.select_related('project__category__profile').prefetch_related('predecessors').filter(project_id=project.pk)
                cpmreport = CPMReport.objects.create(
                    name=title,
                    project=project
                )
                data = []
                for task in tasks:
                    activity = {}
                    activity['activity'] = task.name
                    activity['start_date'] = task.start_date
                    activity['end_date'] = task.end_date
                    activity['duration'] = abs((task.end_date - task.start_date).days)
                    activity['predecessors'] = []
                    for pr in task.predecessors.all():
                        activity['predecessors'].append(pr.name)
                    data.append(activity)
                critical_path = calculate_cpm(data)
                for item in critical_path:
                    print(item)
                    CPMReportData.objects.create(
                        cpmreport=cpmreport,
                        task=Task.objects.get(name=item['activity']),
                        slack=item['slack'],
                        es = item['es'],
                        ef = item['ef'],
                        ls = item['ls'],
                        lf = item['lf']
                    )
            except Project.DoesNotExist:
                pass
        context = self.get_context_data()
        if is_ajax(request):
            html_form = render_to_string(
                self.ajax_list_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset


class CPMReportDetailView(LoginRequiredMixin,DetailView):
    model = CPMReport
    queryset = CPMReport.objects.select_related('project__category__profile').prefetch_related('cpmreportdata_set__task__predecessors')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset