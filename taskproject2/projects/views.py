import datetime
import plotly.express as px
from django.core.files import File
import os
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import tempfile
from django.conf import settings

from django.http import HttpResponse
from weasyprint import HTML


from core.views import *

from core.functions import is_ajax
from core.mixins import *
from projects.models import *
from projects.forms import *
from projects.utils import *


class CategoryListView(BaseListView,QueryMixin):
    model = Category
    paginate_by = 100  # if pagination is desired

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class CategoryDetailView(BaseDetailView):
    model = Category

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset



class CategoryCreateView(BaseCreateView):
    model = Category
    form_class = CategoryForm

    def form_valid(self,form):
        form.instance.profile = self.request.user.profile
        form.save()
        return super().form_valid(form)


class CategoryUpdateView(BaseUpdateView):
    model = Category
    form_class = CategoryForm


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset



class CategoryDeleteView(BaseDeleteView):
    model = Category
    ajax_partial = 'partials/ajax_delete_modal.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class ProjectListView(BaseListView):

    model = Project
    paginate_by = 100  # if pagination is desired
    queryset = Project.objects.prefetch_related('category__company__profiles').select_related('parent')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(category__company__profiles=self.request.user.profile.id)
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

class ProjectDetailView(BaseDetailView):
    model = Project
    queryset = Project.objects.prefetch_related('category__company__profiles')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('category__company__profiles').filter(category__company__profiles=self.request.user.profile.id)
        return queryset


class ProjectCreateView(BaseCreateView):
    model = Project
    form_class = ProjectForm




class ProjectUpdateView(BaseUpdateView):
    model = Project
    form_class = ProjectForm
    queryset = Project.objects.prefetch_related('company__profiles')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('company__profiles').filter(company__profiles=self.request.user.profile.id)
        return queryset


class ProjectDeleteView(BaseDeleteView):
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
    queryset = Task.objects.select_related('project__category__company').prefetch_related('project__category__company__profiles','predecessors')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__company__profiles=self.request.user.profile.pk)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context

class TaskDetailView(BaseDetailView):
    model = Task
    queryset = Task.objects.select_related('project__category__company').prefetch_related('project__category__company__profiles','predecessors')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__company__profiles=self.request.user.profile.pk)
        return queryset


class TaskCreateView(BaseCreateView):
    model = Task
    form_class = TaskForm
    
    
    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'project':self.request.GET.get('project')
        })
        return initial
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formsets'] = [
            {
                'title': 'Predecessors',
                'formset': PredecessorFormSet(
                    self.request.POST or None,
                    queryset=Predecessor.objects.select_related(
                        'from_task', 'to_task')),
                "sb_urls": [{"name":"to_task","url":reverse("projects:get_tasks_for_sb")}]
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


class TaskUpdateView(BaseUpdateView):
    model = Task
    form_class = TaskForm
    queryset = Task.objects.select_related('project__category__company').prefetch_related('project__category__company__profiles','predecessors')


    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__company__profiles=self.request.user.profile.pk)
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
                "sb_urls": [{"name":"to_task","url":reverse("projects:get_tasks_for_sb")}]
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


class TaskDeleteView(BaseDeleteView):
    model = Task
    success_url = reverse_lazy('projects:task-list')
    ajax_partial = 'partials/ajax_delete_modal.html'
    queryset = Task.objects.select_related('project__category__profile')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__profile_id=self.request.user.profile.pk)
        return queryset




    




class CPMReportListView(BaseListView):
    model = CPMReport
    paginate_by = 10  # if pagination is desired
    queryset = CPMReport.objects.prefetch_related('project__category__company__profiles')

    def dispatch(self, *args, **kwargs):
        self.ajax_partial = '{}/partials/{}_list_partial.html'.format(self.model._meta.app_label,self.model.__name__.lower())
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        project_id = request.GET.get('project')
        if project_id:
            generate_cpm_report(self.request,project_id)

        context = self.get_context_data()
        if is_ajax(request):
            html_form = render_to_string(
                self.ajax_partial, context, request)
            return JsonResponse(html_form, safe=False)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__company__profiles=self.request.user.profile.pk)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['template'] = self.ajax_partial
        context['search'] = self.request.GET.get('search','')
        return context


class CPMReportDetailView(BaseDetailView):
    model = CPMReport
    queryset = CPMReport.objects.prefetch_related('project__category__company__profiles','cpmreportdata_set__task__predecessors')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
                project__category__company__profiles=self.request.user.profile.pk)
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
    
    
    
def add_predecessor(request, task_id):
    task = Task.objects.select_related('project__category__company')\
        .prefetch_related('project__category__company__profiles', 'predecessors')\
        .get(id=task_id, project__category__company__profiles=request.user.profile)

    if request.method == 'POST':
        form = PredecessorForm(request=request, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('projects:project_view', kwargs={"pk": task.project_id}))
        else:
            print(form.errors)
            for field in form.errors:
                if not '__all__' in field:
                    try:
                        form.fields[field].widget.attrs['class'] += ' is-invalid'
                    except KeyError:
                        form.fields[field].widget.attrs['class'] = 'is-invalid'

            for error in form.non_field_errors():
                print(error)
    else:
        form = PredecessorForm(request=request, initial={"to_task": task})

    return render(request, 'projects/add_predecessor.html', {'form': form})



def delete_predecessor(request,task,id):
    task = Task.objects.prefetch_related('predecessors').get(id=task)
    task.predecessors.remove(id)
    return redirect(reverse_lazy('projects:project_list'))



def download_full_project_report_pdf(request, project_id):
    project = Project.objects.prefetch_related('tasks').get(id=project_id)
    tasks = project.tasks.all()

    total_cost = sum(task.budget or 0 for task in tasks)
    start_date = tasks.order_by('start_date').first().start_date
    end_date = tasks.order_by('-end_date').first().end_date
    # Get latest CPM report
    cpm_report = CPMReport.objects.filter(project=project).order_by('-created').first()
    # If no CPMReport exists yet, generate it first
    data = generate_cpm_report(request, project.id)
    if not cpm_report:
        cpm_report = CPMReport.objects.filter(project=project).order_by('-created').first()
    # Make sure critical_path image exists
    critical_path_image_url = cpm_report.cpm_graph.url if cpm_report and cpm_report.cpm_graph else None

    # Generate Gantt images if missing
    gantt_folder = os.path.join(settings.MEDIA_ROOT, 'gantt_pages', f'project_{project.id}')
    if not os.path.exists(gantt_folder) or not os.listdir(gantt_folder):
        os.makedirs(gantt_folder, exist_ok=True)
        # Prepare data for Gantt
        cpm_data = []
        for task in tasks:
            cpm_data.append({
                "activity": task.name,
                "predecessors": [pred.from_task.name for pred in task.predecessor_tasks.all()],
                "duration": (task.end_date - task.start_date).days,
                "es": task.early_start,
                "ef": task.early_finish,
                "ls": task.late_start,
                "lf": task.late_finish,
                "slack": task.slack,
            })

        draw_paginated_gantt_chart(cpm_data, save_folder=gantt_folder, page_size=100)

    # Now collect gantt images
    gantt_images = []
    if os.path.exists(gantt_folder):
        for filename in sorted(os.listdir(gantt_folder)):
            if filename.endswith('.png'):
                gantt_images.append(f'/media/gantt_pages/project_{project.id}/{filename}')

    print(gantt_images)
    # Prepare context for HTML
    context = {
        'project': project,
        'tasks': tasks,
        'total_cost': total_cost,
        'start_date': start_date,
        'end_date': end_date,
        'today': datetime.datetime.now().strftime('%Y-%m-%d'),
        'critical_path_image_url': critical_path_image_url,
        'gantt_images': gantt_images,
    }

    html_string = render_to_string('projects/full_project_report.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_full_report.pdf"'

    return response
