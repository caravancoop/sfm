import json
import csv

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import get_language

from complex_fields.models import ComplexFieldContainer

from sfm_pc.base_views import BaseUpdateView, BaseCreateView, BaseDetailView

from .models import Violation, ViolationType, ViolationPerpetratorClassification
from .forms import ViolationBasicsForm, ViolationCreateBasicsForm, ViolationLocationsForm

class ViolationDetail(BaseDetailView):
    model = Violation
    template_name = 'violation/view.html'
    slug_field = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Generate link to download a CSV of this record
        params = '?download_etype=Violation&entity_id={0}'.format(str(context['violation'].uuid))

        context['download_url'] = reverse('download') + params

        context['location'] = None

        if context['violation'].location.get_value():
            location = context['violation'].location.get_value()
            if location.value:
                context['location'] = location.value

        return context


class ViolationEditView(BaseUpdateView):
    model = Violation
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'violation'

    def get_success_url(self):
        uuid = self.kwargs[self.slug_field_kwarg]
        return reverse('view-violation', kwargs={'slug': uuid})


class ViolationEditBasicsView(ViolationEditView):
    template_name = 'violation/edit-basics.html'
    form_class = ViolationBasicsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['basics'] = True

        return context

    def get_success_url(self):
        violation_id = self.kwargs['slug']

        if self.request.POST.get('_continue'):
            return reverse('edit-violation', kwargs={'slug': violation_id})
        else:
            return super().get_success_url()


class ViolationCreateBasicsView(BaseCreateView):
    model = Violation
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'violation'
    template_name = 'violation/create-basics.html'
    form_class = ViolationCreateBasicsForm

    def form_valid(self, form):
        form.save(commit=True)
        return HttpResponseRedirect(reverse('view-violation',
                                            kwargs={'slug': form.object_ref.uuid}))

    def get_success_url(self):
        # This method doesn't ever really get called but since Django does not
        # seem to recognize when we place a get_absolute_url method on the model
        # and some way of determining where to redirect after the form is saved
        # is required, here ya go. The redirect actually gets handled in the
        # form_valid method above.
        return '{}?entity_type=Violation'.format(reverse('search'))


class ViolationEditLocationsView(ViolationEditView):
    template_name = 'violation/edit-locations.html'
    form_class = ViolationLocationsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['locations'] = []

        if context['violation'].location.get_value():
            context['locations'].append(context['violation'].location.get_value().value)

        if context['violation'].adminlevel1.get_value():
            context['locations'].append(context['violation'].adminlevel1.get_value().value)

        if context['violation'].adminlevel2.get_value():
            context['locations'].append(context['violation'].adminlevel2.get_value().value)

        return context

    def get_success_url(self):
        violation_id = self.kwargs['slug']

        if self.request.POST.get('_continue'):
            return reverse('edit-violation', kwargs={'slug': violation_id})
        else:
            return super().get_success_url()


def violation_type_autocomplete(request):
    term = request.GET.get('q')
    types = ViolationType.objects.filter(value__icontains=term).distinct('value').order_by('value')

    results = {
        'results': []
    }
    for violation_type in types:

        results['results'].append({
            'text': violation_type.value,
            'id': violation_type.id,
        })

    return HttpResponse(json.dumps(results), content_type='application/json')


def violation_perpetrator_classification_autocomplete(request):
    term = request.GET.get('q')
    classifications = ViolationPerpetratorClassification.objects.filter(value__icontains=term).distinct('value').order_by('value')

    results = {
        'results': []
    }

    for classification in classifications:

        if classification.value:
            results['results'].append({
                'text': classification.value,
                'id': classification.id,
            })

    return HttpResponse(json.dumps(results), content_type='application/json')


def violation_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="violations.csv"'

    terms = request.GET.dict()
    violation_query = Violation.search(terms)

    writer = csv.writer(response)
    for violation in violation_query:
        writer.writerow([
            violation.id,
            violation.description.get_value(),
            repr(violation.startdate.get_value()),
            repr(violation.enddate.get_value()),
            violation.locationdescription.get_value(),
            violation.adminlevel1.get_value(),
            violation.adminlevel2.get_value(),
            violation.osmname.get_value(),
            violation.osmid.get_value(),
            violation.location.get_value(),
            violation.perpetrator.get_value(),
            violation.perpetratororganization.get_value(),
        ])

    return response

