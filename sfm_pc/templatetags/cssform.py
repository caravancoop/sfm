from django import template

register = template.Library()


@register.filter(name='plusmcf')
def plusmcf(value):
    if value.field.__class__.__name__ == 'ModelChoiceField':
        return value.as_widget(attrs={'class': 'form-control addplus'})
    elif not value.field.__class__.__name__ == 'BooleanField' and not value.field.__class__.__name__ == 'FileField':
        return value.as_widget(attrs={'class': 'form-control'})
    else:
        return value.as_widget()
