from django.template import Library

register = Library()

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    if kwargs.items():
        for k,v in kwargs.items():
            updated[k] = v
    return updated.urlencode()

@register.simple_tag
def simple_query_transform(request, param, value):
    '''
    A verison of `query_transform` that takes two arguments (a param key and its
    value) instead of kwargs. Useful for making URLs out of dynamically-generated
    template variables.
    '''
    updated = request.GET.copy()
    updated[param] = value
    return updated.urlencode()
