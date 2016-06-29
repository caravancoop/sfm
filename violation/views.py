import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import get_language

from extra_views import FormSetView
from cities.models import Place, City, Country, Region, Subregion, District

from violation.models import Violation, Type
from source.models import Source
from person.models import Person
from organization.models import Organization
from violation.forms import ZoneForm, ViolationForm
from sfm_pc.utils import deleted_in_str

class ViolationCreate(FormSetView):
    template_name = 'violation/create.html'
    form_class = ViolationForm
    success_url = reverse_lazy('dashboard')
    extra = 1
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding an event, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect(reverse_lazy('create-source'))
        else:
            return super().dispatch(*args, **kwargs)

   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        organizations = self.request.session.get('organizations')
        people = self.request.session.get('people')

        context['types'] = Type.objects.all()
        context['people'] = people         
        context['organizations'] = organizations
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        return context

    def post(self, request, *args, **kwargs):
        organizations = self.request.session['organizations']

        ViolationFormset = self.get_formset()
        formset = ViolationFormset(request.POST)

        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            startdate = formset.data[form_prefix + 'startdate']
            enddate = formset.data[form_prefix + 'enddate']
            locationdescription = formset.data[form_prefix + 'locationdescription']
            geoid = formset.data[form_prefix + 'geoname']
            geotype = formset.data[form_prefix + 'geotype']
            description = formset.data[form_prefix + 'description']
            perpetrators = formset.data[form_prefix + 'perpetrators']
            orgs = formset.data[form_prefix + 'orgs']
            vtype = formset.data[form_prefix + 'vtype'] 

            newtype, flag = Type.objects.get_or_create(id=vtype)

            if geotype == 'country':
                geo = Country.objects.get(id=geoid)
                admin1 = None
                admin2 = None
                coords = None
            elif geotype == 'region':
                geo = Region.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
            elif geotype == 'subregion':
                geo = Subregion.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
            elif geotype == 'city':
                geo = City.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location
            else:
                geo = District.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location

            violation_data = {
                'Violation_ViolationDescription': {
                   'value': description,
                   'sources': [source],
                   'confidence': 1
                },
                'Violation_ViolationLocationDescription': {
                    'value': locationdescription,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationType': {
                    'value': newtype,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationPerpetrator': {
                    'value': Person.objects.get(id=perpetrators),
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationPerpetratorOrganization': {
                    'value': Organization.objects.get(id=orgs),
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationAdminLevel1': {
                    'value': admin1,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationAdminLevel2': {
                    'value': admin2,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationGeoname': {
                    'value': geo.name,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationGeonameId': {
                    'value': geo.id,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationLocation': {
                    'value': coords,
                    'sources': [source],
                    'confidence': 1
                }
            }
            Violation.create(violation_data)
        response = super().formset_valid(formset)
        return response


class ViolationDelete(DeleteView):
    model = Violation
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(ViolationDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context

    def get_object(self, queryset=None):
        obj = super(ViolationDelete, self).get_object()

        return obj


class ViolationView(TemplateView):
    template_name = 'violation/search.html'

    def get_context_data(self, **kwargs):
        context = super(ViolationView, self).get_context_data(**kwargs)

        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context

def violation_type_autocomplete(request):
    term = request.GET.get('q')
    types = ViolationType.objects.filter(value__code__icontains=term)\
                                 .filter(lang=get_language()).all()

    results = []
    for violation_type in types:
        results.append({
            'text': violation_type.get_value(),
            'id': violation_type.id,
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
            violation.geoname.get_value(),
            violation.geonameid.get_value(),
            violation.location.get_value(),
            violation.perpetrator.get_value(),
            violation.perpetratororganization.get_value(),
        ])

    return response

class ViolationUpdate(TemplateView):
    template_name = 'violation/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            violation = Violation.objects.get(pk=kwargs.get('pk'))
        except Violation.DoesNotExist:
            msg = "This violation does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = violation.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        violation.update(data)

        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(ViolationUpdate, self).get_context_data(**kwargs)
        violation = Violation.objects.get(pk=context.get('pk'))
        context['violation'] = violation
        data = {"value": violation.location.get_value().value}
        context['point'] = ZoneForm(data)

        return context
