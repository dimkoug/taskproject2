from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured


class ProtectedViewMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
                return redirect('%s?next=%s' % (
                                settings.LOGIN_URL, self.request.path))
        return super().dispatch(request, *args, **kwargs)


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse_lazy('{}-list'.format(
            self.model.__name__.lower()))


class ModelMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model': self.model
        })
        return context


class UserSaveMixin:
    def form_valid(self, form):
        form.instance.profile = self.request.user.profiles
        return super().form_valid(form)


class UserObjectMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(profile=self.request.user.profiles)
        return queryset


class UserDeleteMixin:
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.profile == self.request.user.profiles:
            self.object.delete()
        else:
            logout(request)
            return redirect('%s?next=%s' % (
                settings.LOGIN_URL, self.request.path))
        return HttpResponseRedirect(self.get_success_url())
