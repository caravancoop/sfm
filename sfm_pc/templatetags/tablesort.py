from django.template import Library

register = Library()

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for k,v in kwargs.items():
        updated[k] = v
    return updated.urlencode()
