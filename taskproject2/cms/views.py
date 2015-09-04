from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView


from .mixins import (
    SuccessUrlMixin, ModelMixin, ProtectedViewMixin, UserSaveMixin,
    UserObjectMixin, UserDeleteMixin)


class BaseListView(UserObjectMixin, ProtectedViewMixin, ModelMixin, ListView):
    template_name_suffix = '/list'


class BaseDetailView(ProtectedViewMixin, ModelMixin, DetailView):
    template_name_suffix = '/detail'


class BaseCreateView(ProtectedViewMixin, SuccessUrlMixin, UserSaveMixin,
                     ModelMixin,  CreateView):
    template_name_suffix = '/form'


class BaseUpdateView(ProtectedViewMixin, SuccessUrlMixin, UserSaveMixin,
                     ModelMixin, UpdateView):
    template_name_suffix = '/form'


class BaseDeleteView(UserDeleteMixin, ProtectedViewMixin, SuccessUrlMixin,
                     UserSaveMixin, ModelMixin, DeleteView):
    template_name_suffix = '/delete'
