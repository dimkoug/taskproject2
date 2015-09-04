from django.views.generic import TemplateView

from core.mixins import ProtectedViewMixin


class Home(ProtectedViewMixin, TemplateView):
    template_name = 'index.html'
