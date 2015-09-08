from django.shortcuts import render
from django.views.generic.base import TemplateView

from complex_fields.models import ComplexFieldContainer
from sfm_pc.utils import class_for_name

class SourceView(TemplateView):
    template_name = 'modals/source.html'

    def get_context_data(self, **kwargs):
        context = super(SourceView, self).get_context_data(**kwargs)

        field = ComplexFieldContainer.field_from_str_and_id(
            context.get('object_type'),
            context.get('object_id'),
            context.get('field_name'),
        )
        context['field'] = field

        return context

class TranslationView(TemplateView):
    template_name = 'modals/translate.html'

    def get_context_data(self, **kwargs):
        context = super(TranslationView, self).get_context_data(**kwargs)

        field = ComplexFieldContainer.field_from_str_and_id(
            context.get('object_type'),
            context.get('object_id'),
            context.get('field_name'),
        )

        context['field'] = field

        return context

