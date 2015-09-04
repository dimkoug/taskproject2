from django import template
from django.urls import reverse_lazy
register = template.Library()


@register.simple_tag(takes_context=True)
def get_url(context, action, obj=None):
    model = context['model']
    app = model._meta.app_label
    if not obj:
        lower_name = model.__name__.lower()
        url_string = '{}:{}-{}'.format(app, lower_name, action)
        url = reverse_lazy(url_string)
    else:
        lower_name = obj.__class__.__name__.lower()
        url_string = '{}:{}-{}'.format(app, lower_name, action)
        url = reverse_lazy(url_string, kwargs={'uuid': obj.uuid})

    return url
