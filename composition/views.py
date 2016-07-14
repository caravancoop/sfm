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

from composition.models import Composition, Classification
from composition.forms import CompositionForm
from sfm_pc.utils import deleted_in_str
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView

class CompositionCreate(BaseFormSetView):
    template_name = 'composition/edit.html'
    form_class = CompositionForm
    success_url = reverse_lazy('create-person')
    extra = 1
    max_num = None
    
    def get_context_data(self, **kwargs):
        
        # For each organization added, we need to have the ability to
        # add several relationships. Maybe wrap formset loop in
        # template in outer loop that loops through Organizations
        # added?

        context = super().get_context_data(**kwargs)
        
        context['classifications'] = Classification.objects.all()
        context['relationship_types'] = self.form_class().fields['relationship_type'].choices
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        context['organizations'] = self.request.session['organizations']

        return context

    def formset_valid(self, formset):
        
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

