from django.http import JsonResponse
from django.db.models import Q
from core.functions import get_sb_data
from projects.models import Category,Project, Task
from projects.forms import TaskForm


def get_sb_categories_data(request):
    if request.user.is_anonymous:
        return JsonResponse({"results":[]},safe=False)
    queryset = Category.objects.prefetch_related('company__profiles').filter(company__profiles__in=[request.user.profile])
    q_objects = Q()
    d_objects = []
    q = request.GET.get('search')
    for f in  Category._meta.get_fields():
        if f.__class__.__name__  in ['CharField', 'TextField']:
            str_q = f"Q({f.name}__icontains=str('{q}'))"
            q_obj = eval(str_q)
            q_objects |= q_obj
    data = queryset.filter(q_objects)
    for d in data:
        d_objects.append({
            "id": d.pk,
            "text": d.__str__()
        })
    return JsonResponse({"results":d_objects},safe=False)


def get_sb_projects_data(request):
    if request.user.is_anonymous:
        return JsonResponse({"results":[]},safe=False)
    queryset = Project.objects.prefetch_related('company__profiles').filter(company__profiles=request.user.profile)
    q_objects = Q()
    d_objects = []
    q = request.GET.get('search')
    for f in  Category._meta.get_fields():
        if f.__class__.__name__  in ['CharField', 'TextField']:
            str_q = f"Q({f.name}__icontains=str('{q}'))"
            q_obj = eval(str_q)
            q_objects |= q_obj
    data = queryset.filter(q_objects)
    for d in data:
        d_objects.append({
            "id": d.pk,
            "text": d.__str__()
        })
    return JsonResponse({"results":d_objects},safe=False)


def get_tasks_for_sb(request):
    """"
    Return Data for  select box 2  plugin
    """
    results = []
    if not request.user.is_authenticated:
        return JsonResponse(results, safe=False)
    search = request.GET.get('search')
    if search and search != '':
        data = Task.objects.prefetch_related('company__profiles').filter(
            Q(name__icontains=search),company__profiles=request.user.profile.pk
        ).values('id', 'name')
        for d in data:
            results.append({'id':d['id'], "text": d['name']})
        # j_data = serializers.serialize("json", data, fields=('erp_code', 'title'))
        # return JsonResponse(j_data, safe=False)
    return JsonResponse({"results": results}, safe=False)



def add_task(request,project_id):
    project = Project.objects.prefetch_related('company__profiles').get(id=project_id,company__profiles=request.user.profile)
    task = TaskForm(initial={"company":project.company,"project":project})
