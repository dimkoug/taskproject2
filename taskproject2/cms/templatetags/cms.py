from django import template
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def create_title(model, value):
    """
    example:  category add
    """
    model_name = model.__class__.__name__
    return '{} {}'.format(model_name, value)


@register.simple_tag
def create_url(model, value):
    """
    example:  category-create
    """
    model_name = model.__class__.__name__.lower()
    url = "{}-{}".format(model_name, value)
    return reverse_lazy(url)


@register.simple_tag
def create_caption(model, value):
    """
    example:  Create Category
    """
    caption = value
    model_name = model.__class__.__name__.lower()
    title = '{} {}'.format(caption, model_name)
    return mark_safe(title.title())


@register.simple_tag
def update_url(model, value):
    """
    example:  category-update
    """
    model_name = model.__class__.__name__.lower()
    url = "{}-{}".format(model_name, value)
    return reverse_lazy(url, kwargs={'pk': model.pk})


@register.simple_tag
def detail_url(model, value):
    """
    example:  category-detail
    """
    model_name = model.__class__.__name__.lower()
    url = "{}-{}".format(model_name, value)
    return reverse_lazy(url, kwargs={'pk': model.pk})


@register.simple_tag
def delete_url(model, value):
    """
    example:  category-delete
    """
    model_name = model.__class__.__name__.lower()
    url = "{}-{}".format(model_name, value)
    return reverse_lazy(url, kwargs={'pk': model.pk})


@register.simple_tag
def list_url(model, value):
    """
    example:  category-list
    """
    model_name = model.__class__.__name__.lower()
    url = "{}-{}".format(model_name, value)
    return reverse_lazy(url)
