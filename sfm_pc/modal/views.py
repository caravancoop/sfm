from django.shortcuts import render
from django.views.generic.base import TemplateView

from sfm_pc.utils import class_for_name

class SourceView(TemplateView):
    template_name = 'modals/source.html'

    def get_context_data(self, **kwargs):
        context = super(SourceView, self).get_context_data(**kwargs)

        object_name = context.get('object_type')
        object_class = class_for_name(object_name.capitalize(), object_name + ".models")
        object_ = object_class.from_id(context.get('object_id'))
        field = getattr(object_, context.get('field_name'))
        context['field'] = field

        return context

