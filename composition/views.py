import json
from itertools import combinations

from django import forms
from django.conf import settings
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from source.models import Source
from organization.models import Organization
from composition.models import Composition, Classification
from composition.forms import CompositionForm, BaseCompositionFormSet
from sfm_pc.base_views import BaseFormSetView


class CompositionCreate(BaseFormSetView):
    template_name = 'composition/create.html'
    form_class = CompositionForm
    formset_class = BaseCompositionFormSet
    success_url = reverse_lazy('create-organization-membership')
    extra = 0
    max_num = None

    def get_org_pairs(self, orgs):

        org_ids = [org['id'] for org in orgs]

        return list(combinations(org_ids, 2))

    def get_initial(self):

        data = []

        created_orgs = self.request.session.get('organizations')

        if created_orgs:
            # Generate forms for each unique combination of orgs
            org_pairs = self.get_org_pairs(created_orgs)

            for pair in org_pairs:
                data.append({})

        return data

    def get(self, request, *args, **kwargs):
        if self.request.session.get('organizations'):
            if len(request.session['organizations']) == 1:
                return redirect(reverse_lazy('create-organization-membership'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['confidence_levels'] = settings.CONFIDENCE_LEVELS
        context['open_ended_choices'] = settings.OPEN_ENDED_CHOICES

        context['classifications'] = Classification.objects.all()
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        context['organizations'] = self.request.session.get('organizations')

        context['org_pairs'] = self.get_org_pairs(context['organizations'])

        context['back_url'] = reverse_lazy('create-organization')
        context['skip_url'] = reverse_lazy('create-organization-membership')

        existing_forms = self.request.session.get('forms', {})

        if existing_forms and existing_forms.get('compositions') and not getattr(self, 'formset', False):

            form_data = existing_forms.get('compositions')
            self.initFormset(form_data)

            context['formset'] = self.formset
            context['browsing'] = True

        return context

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])

        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)

            composition_info = {}

            # Dates
            startdate_confidence = int(formset.data.get(form_prefix +
                                                        'startdate_confidence', 1))
            enddate_confidence = int(formset.data.get(form_prefix +
                                                      'enddate_confidence', 1))

            startdate = formset.data.get(form_prefix + 'startdate')
            realstart = formset.data.get(form_prefix + 'realstart'):
            enddate = formset.data.get(form_prefix + 'enddate')
            open_ended = formset.data.get(form_prefix + 'open_ended', 'N')

            if startdate:

                composition_info['Composition_CompositionStartDate'] = {
                    'value': startdate,
                    'confidence': startdate_confidence,
                    'sources': [source]
                }


                if realstart:
                    realstart = True
                else:
                    realstart = False

                composition_info['Composition_CompositionRealStart'] = {
                    'value': realstart,
                    'confidence': startdate_confidence,
                    'sources': [source]
                }


            if enddate:

                composition_info['Composition_CompositionEndDate'] = {
                    'value': enddate,
                    'confidence': enddate_confidence,
                    'sources': [source]
                }

            # We want to record a value for open_ended no matter what, since
            # it can't be null. 'N' is effectively the null value, and form
            # validation enforces the proper logic with regard to the existence
            # of the enddate field.
            composition_info['Composition_CompositionOpenEnded'] = {
                'value': formset.data[form_prefix + 'open_ended'],
                'confidence': enddate_confidence,
                'sources': [source]
            }

            # Relationship classification
            classification_id = formset.data[form_prefix + 'classification']
            classification = Classification.objects.get(id=classification_id)
            classification_confidence = int(formset.data.get(form_prefix +
                                                             'classification_confidence', 1))

            composition_info['Composition_CompositionClassification'] = {
                'value': classification,
                'confidence': classification_confidence,
                'sources': [source]
            }

            # Parent and child orgs
            parent_id = formset.data[form_prefix + 'parent']
            parent = Organization.objects.get(id=parent_id)
            parent_confidence = int(formset.data.get(form_prefix +
                                                     'parent_confidence', 1))

            child_id = formset.data[form_prefix + 'child']
            child = Organization.objects.get(id=child_id)
            child_confidence = int(formset.data.get(form_prefix +
                                                    'child_confidence', 1))

            composition, created = Composition.objects.get_or_create(compositionparent__value=parent,
                                                                     compositionchild__value=child)

            if created:
                parent_sources = [source]
                child_sources = parent_sources
            else:
                self.source = source
                parent_sources = self.sourcesList(composition, 'parent')
                child_sources = self.sourcesList(composition, 'child')

            composition_info['Composition_CompositionParent'] = {
                'value': parent,
                'confidence': parent_confidence,
                'sources': parent_sources
            }
            composition_info['Composition_CompositionChild'] = {
                'value': child,
                'confidence': child_confidence,
                'sources': child_sources
            }

            composition.update(composition_info)

        if not self.request.session.get('forms'):
            self.request.session['forms'] = {}

        self.request.session['forms']['compositions'] = formset.data

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
