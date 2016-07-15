import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.contrib.admin.utils import NestedObjects
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from source.models import Source
from organization.models import Organization
from composition.models import Composition, Classification
from composition.forms import CompositionForm
from sfm_pc.utils import deleted_in_str
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView

class CompositionCreate(BaseFormSetView):
    template_name = 'composition/create.html'
    form_class = CompositionForm
    success_url = reverse_lazy('create-person')
    extra = 0
    max_num = None
    
    def get_initial(self):
        data = []
        for i in self.request.session['organizations']:
            data.append({})
        return data

    def get(self, request, *args, **kwargs):
        if len(request.session['organizations']) == 1:
            return redirect(reverse_lazy('create-person'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        
        context['classifications'] = Classification.objects.all()
        context['relationship_types'] = self.form_class().fields['relationship_type'].choices
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        context['organizations'] = self.request.session['organizations']

        return context

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        
        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            
            composition_info = {}

            organization_id = formset.data[form_prefix + 'organization']
            organization = Organization.objects.get(id=organization_id)
            
            rel_type = formset.data[form_prefix + 'relationship_type']
            if rel_type == 'child':
                composition_info['Composition_CompositionChild'] = {
                    'value': organization,
                    'confidence': 1,
                    'sources': [source]
                }
            elif rel_type == 'parent':
                composition_info['Composition_CompositionParent'] = {
                    'value': organization,
                    'confidence': 1,
                    'sources': [source]
                }

            if formset.data.get(form_prefix + 'startdate'):
                composition_info['Composition_CompositionStartDate'] = {
                    'value': formset.data[form_prefix + 'startdate'],
                    'confidence': 1,
                    'sources': [source]
                }
            
            if formset.data.get(form_prefix + 'enddate'):
                composition_info['Composition_CompositionEndDate'] = {
                    'value': formset.data[form_prefix + 'enddate'],
                    'confidence': 1,
                    'sources': [source]
                }

            classification_id = formset.data[form_prefix + 'classification']
            classification = Classification.objects.get(id=classification_id)

            composition_info['Composition_CompositionClassification'] = {
                'value': classification,
                'confidence': 1,
                'sources': [source]
            }

            composition = Composition.create(composition_info)
            
        response = super().formset_valid(formset)
        return response


class CompositionUpdate(TemplateView):
    template_name = 'composition/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            composition = Composition.objects.get(pk=kwargs.get('pk'))
        except Composition.DoesNotExist:
            msg = "This composition does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = composition.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        composition.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(CompositionUpdate, self).get_context_data(**kwargs)
        context['composition'] = Composition.objects.get(pk=context.get('pk'))

        return context

########################
## Unused views below ##
########################

class CompositionDelete(DeleteView):
    model = Composition
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(CompositionDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context

    def get_object(self, queryset=None):
        obj = super(CompositionDelete, self).get_object()

        return obj


class CompositionView(TemplateView):
    template_name = 'composition/search.html'

    def get_context_data(self, **kwargs):
        context = super(CompositionView, self).get_context_data(**kwargs)

        context['classifications'] = Classification.objects.all()
        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


def composition_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="compositions.csv"'

    terms = request.GET.dict()
    composition_query = Composition.search(terms)

    writer = csv.writer(response)
    for composition in composition_query:
        writer.writerow([
            composition.id,
            composition.parent.get_value(),
            composition.child.get_value(),
            composition.classification.get_value(),
            repr(composition.startdate.get_value()),
            repr(composition.enddate.get_value()),
        ])

    return response

