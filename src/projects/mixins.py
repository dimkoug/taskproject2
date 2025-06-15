from django.db.models import Q


class SearchMixin:
    def get_queryset(self):
        model = self.model.__name__.lower()
        queryset = super().get_queryset()
        search = self.request.GET.get('q')
        if search != "" and search:
            if model == 'category':
                queryset = queryset.filter(title__icontains=search)
            if model == 'project':
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(category__title__icontains=search))
            if model == 'task':
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(project__title__icontains=search))
        return queryset
