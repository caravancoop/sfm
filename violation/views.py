import csv
from datetime import date
from itertools import chain
import json

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import get_language, gettext as _

from complex_fields.models import ComplexFieldContainer

from sfm_pc.base_views import BaseUpdateView, BaseCreateView, BaseDetailView, BaseDeleteView

from .models import Violation, ViolationType, ViolationPerpetratorClassification
from .forms import ViolationBasicsForm, ViolationCreateBasicsForm, ViolationLocationsForm


class ViolationDetail(BaseDetailView):
    model = Violation
    template_name = 'violation/view.html'
    slug_field = 'uuid'

    def get_sources(self, context):
        return context['violation'].sources.order_by('source_url', '-accesspoint__accessed_on')\
                                           .distinct('source_url')

    def get_page_title(self):
        title = _('Incident')

        if self.object.osmname.get_value():
            title += ' {0} {1}'.format(_('in'), self.object.osmname.get_value())

        start = self.object.startdate.get_value()
        end = self.object.enddate.get_value()

        if start and end:
            if start.value == end.value:
                title += ' {0} {1}'.format(_('on'), start.value)
            else:
                title += ' {0} {1} {2} {3}'.format(_('between'), start.value, _('and'), end.value)
        elif start:
            title += ' {0} {1}'.format(_('starting'), start.value)
        elif end:
            title += ' {0} {1}'.format(_('ending'), end.value)

        return title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        authenticated = self.request.user.is_authenticated

        # Generate link to download a CSV of this record
        params = '?download_etype=Violation&entity_id={0}'.format(str(context['violation'].uuid))

        context['download_url'] = reverse('download') + params

        context['location'] = None

        if context['violation'].location.get_value():
            location = context['violation'].location.get_value()
            if location.value:
                context['location'] = location.value

        if authenticated:
            context['perpetrators'] = context['violation'].violationperpetrator_set.all()
        else:
            context['perpetrators'] = context['violation'].violationperpetrator_set.filter(value__published=True)

        if authenticated:
            context['perpetrator_organizations'] = context['violation'].violationperpetratororganization_set.all()
        else:
            context['perpetrator_organizations'] = context['violation'].violationperpetratororganization_set.filter(value__published=True)

        context['sources'] = self.get_sources(context)
        context['page_title'] = self.get_page_title()

        return context


class ViolationEditView(BaseUpdateView):
    model = Violation
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    context_object_name = 'violation'

    def get_success_url(self):
        uuid = self.kwargs[self.slug_field_kwarg]
        return reverse('view-violation', kwargs={'slug': uuid})


class ViolationDeleteView(BaseDeleteView):
    model = Violation
    slug_field = 'uuid'
    slug_field_kwarg = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'violation/delete.html'
    context_object_name = 'violation'

    def get_cancel_url(self):
        return reverse_lazy('edit-violation', args=[self.kwargs['slug']])

    def get_success_url(self):
        return reverse('search') + '?entity_type=Violation'

    def get_related_entities(self):
        return self.object.related_entities


class ViolationEditBasicsView(ViolationEditView):
    template_name = 'violation/edit-basics.html'
    form_class = ViolationBasicsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['basics'] = True

        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['violation_id'] = self.kwargs['slug']
        return form_kwargs

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
                'id': classification.value,
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


class ViolationSitemap(Sitemap):

    protocol = 'http' if settings.DEBUG else 'https'

    def items(self):
        return Violation.objects.filter(published=True).order_by('id')

    def location(self, obj):
        return reverse('view-violation', args=[obj.uuid])
