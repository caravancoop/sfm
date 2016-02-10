from django import template

register = template.Library()


@register.filter()
def to_int(value):
    if RepresentsInt(value):
        return int(value)
    else:
        return ''


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
