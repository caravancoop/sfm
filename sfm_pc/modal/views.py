import json

from django.shortcuts import render
from django.views.generic.base import TemplateView

from complex_fields.models import ComplexFieldContainer

class SourceView(TemplateView):
    template_name = 'modals/source.html'

    def get_context_data(self, **kwargs):
        context = super(SourceView, self).get_context_data(**kwargs)

        field = ComplexFieldContainer.field_from_str_and_id(
            context.get('object_type'),
            context.get('object_id'),
            context.get('field_name'),
            context.get('field_id', None)
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
            context.get('field_id', None)
        )

        context['field'] = field

        return context

class VersionView(TemplateView):
    template_name = 'modals/version.html'

    def get_context_data(self, **kwargs):
        context = super(VersionView, self).get_context_data(**kwargs)

        field = ComplexFieldContainer.field_from_str_and_id(
            context.get('object_type'),
            context.get('object_id'),
            context.get('field_name'),
            context.get('field_id', None)
        )

        context['field'] = field
        context['history'] = field.get_history_for_lang()
        context['langs'] = field.get_langs_in_history()

        return context
