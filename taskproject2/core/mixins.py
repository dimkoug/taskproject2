from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


class ProtectedViewMixin:

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect(reverse_lazy('login') + '?next={}'.format(self.request.path))
        return super().dispatch(*args, **kwargs)


class ModelMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        return context
