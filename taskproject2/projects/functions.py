from django.http import JsonResponse
from django.db.models import Q
from core.functions import get_sb_data
from projects.models import Category,Project, Task


def get_sb_categories_data(request):
    if request.user.is_anonymous:
        return JsonResponse({"results":[]},safe=False)
    queryset = Category.objects.select_related('profile').filter(profile_id=request.user.profile)
    q_objects = Q()
    q = request.GET.get('search')
    for f in  Category._meta.get_fields():
        if f.__class__.__name__  in ['CharField', 'TextField']:
            str_q = f"Q({f.name}__icontains=str('{q}'))"
            q_obj = eval(str_q)
            q_objects |= q_obj
    return get_sb_data(queryset,q_objects)


def get_sb_projects_data(request):
    if request.user.is_anonymous:
        return JsonResponse({"results":[]},safe=False)
    queryset = Project.objects.select_related('category__profile').filter(category__profile_id=request.user.profile)
    q_objects = Q()
    q = request.GET.get('search')
    for f in  Project._meta.get_fields():
        if f.__class__.__name__  in ['CharField', 'TextField']:
            str_q = f"Q({f.name}__icontains=str('{q}'))"
            q_obj = eval(str_q)
            q_objects |= q_obj
    return get_sb_data(queryset,q_objects)


def get_tasks_for_sb(request):
    """"
    Return Data for  select box 2  plugin
    """
    results = []
    if not request.user.is_authenticated:
        return JsonResponse(results, safe=False)
    search = request.GET.get('search')
    if search and search != '':
        data = Task.objects.select_related('project__category__profile').filter(
            Q(name__icontains=search),project__category__profile_id=request.user.profile.pk
        ).values('id', 'name')
        for d in data:
            results.append({'id':d['id'], "text": d['name']})
        # j_data = serializers.serialize("json", data, fields=('erp_code', 'title'))
        # return JsonResponse(j_data, safe=False)
    return JsonResponse({"results": results}, safe=False)