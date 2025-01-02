import datetime
import plotly.express as px
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
from core.mixins import PaginationMixin, ModelMixin, SuccessUrlMixin,FormMixin,QueryMixin, AjaxDeleteMixin

from .models import Category, Project, Task, Predecessor, CPMReport,CPMReportData
from .forms import CategoryForm, ProjectForm, TaskForm, PredecessorFormSet,GanttFilterForm
from .calculate_critical_path import calculate_cpm


class BaseListView(PaginationMixin, ModelMixin, LoginRequiredMixin, ListView):
    def dispatch(self, *args, **kwargs):
        self.ajax_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        if is_ajax(request):
            html_form = render_to_string(
                self.ajax_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context




class CategoryListView(BaseListView,QueryMixin):
    model = Category
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class CategoryDetailView(LoginRequiredMixin,ModelMixin,DetailView):
    model = Category

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
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
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset



class CategoryDeleteView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Category
    ajax_partial = 'partials/ajax_delete_modal.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class ProjectListView(BaseListView):

    model = Project
    paginate_by = 100  # if pagination is desired
    queryset = Project.objects.prefetch_related('company__profiles').select_related('parent')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(company__profiles=self.request.user.profile.id)
        category = self.request.GET.get('category')
        parent = self.request.GET.get('parent')
        if category:
            queryset = queryset.filter(category_id=category)
        if parent:
            queryset = queryset.filter(parent_id=parent)

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context

class ProjectDetailView(LoginRequiredMixin,DetailView):
    model = Project
    queryset = Project.objects.prefetch_related('company__profiles')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class ProjectCreateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, CreateView):
    model = Project
    form_class = ProjectForm




class ProjectUpdateView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,FormMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    queryset = Project.objects.prefetch_related('company__profiles')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class ProjectDeleteView(ModelMixin, LoginRequiredMixin,SuccessUrlMixin,AjaxDeleteMixin,DeleteView):
    model = Project
    ajax_partial = 'partials/ajax_delete_modal.html'
    queryset = Project.objects.prefetch_related('company__profiles')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context

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
    queryset = CPMReport.objects.prefetch_related('project__company__profiles')

    def dispatch(self, *args, **kwargs):
        self.ajax_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        project_id = request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.prefetch_related('company__profiles').get(company__profiles=self.request.user.profile.pk,id=project_id)
                title = 'Cpm report'
                tasks = Task.objects.prefetch_related('project__company__profiles','predecessors').filter(project_id=project.pk)
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
                self.ajax_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__company__profiles=self.request.user.profile.pk)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context


class CPMReportDetailView(LoginRequiredMixin,DetailView):
    model = CPMReport
    queryset = CPMReport.objects.prefetch_related('project__company__profiles','cpmreportdata_set__task__predecessors')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__company__profiles=self.request.user.profile.pk)
        return queryset
    

def gantt_chart_view(request, project_id):
    # Fetch the project
    project = Project.objects.get(id=project_id)
    
    # Get filters from the request
    form = GanttFilterForm(request.GET or None)
    
    # Base query
    tasks = Task.objects.filter(project_id=project_id).order_by('start_date')
    
    # Apply filters if the form is valid
    if form.is_valid():
        if form.cleaned_data.get('category'):
            tasks = tasks.filter(project__category=form.cleaned_data['category'])
        if form.cleaned_data.get('start_date'):
            tasks = tasks.filter(start_date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            tasks = tasks.filter(end_date__lte=form.cleaned_data['end_date'])
    
    # Prepare data for Gantt chart
    chart_data = []
    for task in tasks:
        chart_data.append({
            'Task': task.name,
            'Start': task.start_date,
            'Finish': task.end_date,
            'Predecessors': ', '.join([pred.name for pred in task.predecessors.all()]) if task.predecessors.exists() else None,
        })
    
    # Create the Gantt chart
    fig = px.timeline(
        chart_data, 
        x_start="Start", 
        x_end="Finish", 
        y="Task", 
        title=f"Gantt Chart for {project.name}",
        labels={"Task": "Tasks"},
        color_discrete_sequence=["#636EFA"]
    )
    fig.update_yaxes(categoryorder="total ascending")
    gantt_chart_html = fig.to_html(full_html=False)

    # Render the template with the form and chart
    return render(request, 'gantt_chart.html', {
        'form': form,
        'gantt_chart': gantt_chart_html,
    })