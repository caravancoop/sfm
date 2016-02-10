from django.template import Library

register = Library()


@register.filter
def is_in(var, args):
    if args is None:
        return False
    addthisclass = ''
    arg_list = [arg.strip() for arg in args.split(',')]

    if var == arg_list[0] and arg_list[1] == 'DESC':
        addthisclass = '_desc'
    if var == arg_list[0] and arg_list[1] == 'ASC':
        addthisclass = '_asc'

    return addthisclass
